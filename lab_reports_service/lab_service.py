"""
lab_service.py
Core service: OCR extraction + GPT analysis for lab reports.
"""

import re
import json
import logging
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
from openai import OpenAI
from django.conf import settings

logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.OPENAI_API_KEY)


# ─────────────────────────────────────────────
# OCR
# ─────────────────────────────────────────────

def preprocess_image(image_path: str) -> Image.Image:
    """Enhance image for better OCR accuracy."""
    img = Image.open(image_path).convert('L')          # grayscale
    img = img.filter(ImageFilter.SHARPEN)
    img = ImageEnhance.Contrast(img).enhance(2.0)
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    return img


def extract_text_from_image(image_path: str) -> str:
    """Run Tesseract OCR and return cleaned text."""
    img = preprocess_image(image_path)
    custom_config = r'--oem 3 --psm 6'
    raw = pytesseract.image_to_string(img, config=custom_config)
    return raw.strip()


def parse_lab_values(ocr_text: str) -> dict:
    """
    Regex-based extraction of common lab parameters from OCR text.
    Returns a dict of { parameter: {value, unit, reference_range} }.
    """
    patterns = {
        'Hemoglobin':     r'(?:Hb|Hemoglobin|Haemoglobin)\s*[:\-]?\s*([\d.]+)\s*(g/dL|g/L)?',
        'WBC':            r'(?:WBC|White Blood Cell|Leukocytes)\s*[:\-]?\s*([\d.]+)\s*(?:x10[³3]|K/µL|10\^3)?',
        'RBC':            r'(?:RBC|Red Blood Cell|Erythrocytes)\s*[:\-]?\s*([\d.]+)\s*(?:x10[⁶6]|M/µL)?',
        'Platelets':      r'(?:Platelets?|PLT)\s*[:\-]?\s*([\d,]+)\s*(?:x10[³3]|K/µL|/mm3)?',
        'Glucose':        r'(?:Glucose|Blood Sugar|FBS|RBS)\s*[:\-]?\s*([\d.]+)\s*(mg/dL|mmol/L)?',
        'HbA1c':          r'(?:HbA1c|Glycated Hemoglobin|A1C)\s*[:\-]?\s*([\d.]+)\s*%?',
        'Cholesterol':    r'(?:Total Cholesterol|Cholesterol)\s*[:\-]?\s*([\d.]+)\s*(mg/dL)?',
        'HDL':            r'(?:HDL|HDL-C|Good Cholesterol)\s*[:\-]?\s*([\d.]+)\s*(mg/dL)?',
        'LDL':            r'(?:LDL|LDL-C|Bad Cholesterol)\s*[:\-]?\s*([\d.]+)\s*(mg/dL)?',
        'Triglycerides':  r'(?:Triglycerides?|TG)\s*[:\-]?\s*([\d.]+)\s*(mg/dL)?',
        'Creatinine':     r'(?:Creatinine|Serum Creatinine)\s*[:\-]?\s*([\d.]+)\s*(mg/dL)?',
        'BUN':            r'(?:BUN|Blood Urea Nitrogen|Urea)\s*[:\-]?\s*([\d.]+)\s*(mg/dL)?',
        'ALT':            r'(?:ALT|SGPT|Alanine Aminotransferase)\s*[:\-]?\s*([\d.]+)\s*(?:U/L|IU/L)?',
        'AST':            r'(?:AST|SGOT|Aspartate Aminotransferase)\s*[:\-]?\s*([\d.]+)\s*(?:U/L|IU/L)?',
        'TSH':            r'(?:TSH|Thyroid Stimulating Hormone)\s*[:\-]?\s*([\d.]+)\s*(mIU/L|µIU/mL)?',
        'T3':             r'(?:T3|Triiodothyronine|Free T3)\s*[:\-]?\s*([\d.]+)\s*(ng/dL|pg/mL)?',
        'T4':             r'(?:T4|Thyroxine|Free T4)\s*[:\-]?\s*([\d.]+)\s*(µg/dL|ng/dL)?',
        'Sodium':         r'(?:Sodium|Na)\s*[:\-]?\s*([\d.]+)\s*(mEq/L|mmol/L)?',
        'Potassium':      r'(?:Potassium|K)\s*[:\-]?\s*([\d.]+)\s*(mEq/L|mmol/L)?',
        'Calcium':        r'(?:Calcium|Ca)\s*[:\-]?\s*([\d.]+)\s*(mg/dL)?',
        'Vitamin_D':      r'(?:Vitamin D|25-OH|25-Hydroxy)\s*[:\-]?\s*([\d.]+)\s*(ng/mL|nmol/L)?',
        'Vitamin_B12':    r'(?:Vitamin B12|Cobalamin|B12)\s*[:\-]?\s*([\d.]+)\s*(pg/mL|pmol/L)?',
        'Iron':           r'(?:Serum Iron|Iron)\s*[:\-]?\s*([\d.]+)\s*(µg/dL|µmol/L)?',
        'Ferritin':       r'(?:Ferritin)\s*[:\-]?\s*([\d.]+)\s*(ng/mL|µg/L)?',
    }

    extracted = {}
    for param, pattern in patterns.items():
        match = re.search(pattern, ocr_text, re.IGNORECASE)
        if match:
            extracted[param] = {
                'value': match.group(1).replace(',', ''),
                'unit': match.group(2) if match.lastindex >= 2 and match.group(2) else '',
            }
    return extracted


# ─────────────────────────────────────────────
# PRO-LEVEL GPT PROMPT
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """
You are Dr. AI — an expert medical report analyst with clinical training across 
hematology, biochemistry, endocrinology, nephrology, hepatology, and general medicine. 
Your role is to analyze patient lab reports and provide clear, actionable, 
medically accurate interpretations that a layperson can understand.

You ALWAYS respond ONLY in valid JSON format. No markdown, no prose outside JSON.

Your JSON response must follow this exact structure:
{
  "summary": "2-3 sentence plain-language summary of the overall health picture",
  "report_type": "detected report type (e.g. Complete Blood Count, Lipid Panel, etc.)",
  "parameters": [
    {
      "name": "parameter name",
      "value": "numeric value",
      "unit": "unit",
      "status": "normal | high | low | critical_high | critical_low",
      "reference_range": "reference range string",
      "interpretation": "1-2 sentence clinical meaning in plain English",
      "severity": "none | mild | moderate | severe"
    }
  ],
  "abnormal_flags": ["list of parameters that are outside normal range"],
  "critical_alerts": ["list of any critically abnormal values requiring urgent attention"],
  "health_risks": [
    {
      "condition": "condition name",
      "risk_level": "low | moderate | high",
      "explanation": "why this is a concern based on these results"
    }
  ],
  "dietary_recommendations": [
    {
      "recommendation": "specific dietary advice",
      "reason": "why this helps based on results"
    }
  ],
  "lifestyle_recommendations": [
    {
      "recommendation": "specific lifestyle or exercise advice",
      "reason": "why this helps based on results"
    }
  ],
  "follow_up_tests": ["list of tests that should be done as follow-up"],
  "doctor_consult_urgency": "immediate | within_week | within_month | routine",
  "doctor_consult_reason": "reason why they should see a doctor",
  "positive_findings": ["list of parameters that are normal or good"],
  "trend_advice": "advice on what to monitor over time",
  "disclaimer": "Always present — remind user this is AI analysis, not a diagnosis"
}
""".strip()


def build_user_prompt(ocr_text: str, extracted_params: dict, report_type: str = '') -> str:
    params_str = json.dumps(extracted_params, indent=2) if extracted_params else "Not extracted"
    return f"""
Analyze the following lab report.

REPORT TYPE (if known): {report_type or 'Auto-detect from content'}

--- RAW OCR TEXT ---
{ocr_text}

--- PRE-EXTRACTED PARAMETERS (may be incomplete) ---
{params_str}

Instructions:
1. Use both the raw OCR text AND the pre-extracted parameters.
2. If OCR missed values, extract them yourself from the raw text.
3. Determine reference ranges based on standard clinical guidelines.
4. Flag any value that is outside the reference range.
5. Mark critical values (e.g. Hemoglobin < 7, Glucose > 400, Potassium > 6.5) 
   as critical alerts.
6. Provide actionable dietary and lifestyle changes tailored to these results.
7. Be empathetic but factual. Avoid causing unnecessary panic.
8. RESPOND ONLY IN THE JSON FORMAT SPECIFIED IN YOUR SYSTEM PROMPT.
""".strip()


# ─────────────────────────────────────────────
# GPT ANALYSIS
# ─────────────────────────────────────────────

def analyze_with_gpt(ocr_text: str, extracted_params: dict, report_type: str = '') -> dict:
    """
    Send extracted data to GPT-4o and return structured analysis.
    Returns parsed JSON dict on success, or error dict on failure.
    """
    user_prompt = build_user_prompt(ocr_text, extracted_params, report_type)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=2500,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return json.loads(content)

    except json.JSONDecodeError as e:
        logger.error(f"GPT JSON parse error: {e}")
        return {"error": "Failed to parse GPT response", "raw": content}
    except Exception as e:
        logger.error(f"GPT API error: {e}")
        return {"error": str(e)}


def ask_followup_question(report_context: dict, question: str) -> str:
    """
    Answer a follow-up question from a patient about their specific report.
    """
    system = """
You are Dr. AI, a compassionate and knowledgeable medical assistant.
A patient is asking a follow-up question about their lab report.
Answer clearly, empathetically, and in plain English.
Do NOT provide a diagnosis. Explain in a way a non-medical person understands.
Keep response under 300 words. End with a gentle reminder to consult their doctor.
""".strip()

    context_str = json.dumps(report_context, indent=2)
    user_msg = f"""
Lab Report Analysis Context:
{context_str}

Patient Question: {question}
""".strip()

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.4,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Follow-up GPT error: {e}")
        return "Sorry, I couldn't process your question right now. Please try again."


# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────

def process_lab_report(image_path: str, report_type: str = '') -> dict:
    """
    Full pipeline: OCR → parse → GPT analysis.
    Returns: {
        ocr_text, extracted_params, ai_result (structured JSON), error (if any)
    }
    """
    try:
        ocr_text = extract_text_from_image(image_path)
        if not ocr_text or len(ocr_text) < 20:
            return {"error": "Could not extract readable text from image. Please upload a clearer image."}

        extracted_params = parse_lab_values(ocr_text)
        ai_result = analyze_with_gpt(ocr_text, extracted_params, report_type)

        return {
            "ocr_text": ocr_text,
            "extracted_params": extracted_params,
            "ai_result": ai_result,
        }

    except Exception as e:
        logger.exception(f"Lab report processing failed: {e}")
        return {"error": str(e)}