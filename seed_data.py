"""
Django seed script — Hospital entries + linked Users
Run with:  python manage.py shell < seed_hospitals.py
Or paste directly into:  python manage.py shell
"""

import random
from decimal import Decimal
from django.contrib.auth import get_user_model

User = get_user_model()

# ─────────────────────────────────────────────
# 1.  RAW HOSPITAL DATA
# ─────────────────────────────────────────────

HOSPITALS_DATA = [
    # ── Navi Mumbai ──────────────────────────────────────────────────────
    {
        "name": "Kokilaben Dhirubhai Ambani Hospital (Navi Mumbai)",
        "city": "Navi Mumbai", "state": "Maharashtra", "pincode": "400710",
        "address": "Sector 14, Kharghar, Navi Mumbai",
        "latitude": "19.1029024", "longitude": "73.0129370",
        "phone": "022-61606161", "email": "info.nm@kokilabenhospital.com",
        "website": "https://www.kokilabenhospital.com",
        "registration_number": "MH-NM-001",
        "description": "A flagship multi-super-speciality hospital offering world-class tertiary care.",
        "total_beds": 750, "available_beds": 210,
        "icu_total": 80, "icu_available": 18,
        "emergency_beds": 40, "emergency_available": 10,
        "established_year": 2009,
        "departments": ["Cardiology", "Neurology", "Oncology", "Orthopedics", "Gastroenterology"],
        "amenities": ["Pharmacy", "Cafeteria", "Parking", "ATM", "Blood Bank", "Ambulance"],
    },
    {
        "name": "SADGURU Hospital",
        "city": "Navi Mumbai", "state": "Maharashtra", "pincode": "400701",
        "address": "Rabale-Ghansoli Road, Navi Mumbai",
        "latitude": "19.1297806", "longitude": "73.0003888",
        "phone": "022-27692000", "email": "sadguru@hospital.in",
        "website": "",
        "registration_number": "MH-NM-002",
        "description": "Trusted multi-speciality hospital serving Navi Mumbai since 2001.",
        "total_beds": 200, "available_beds": 60,
        "icu_total": 20, "icu_available": 5,
        "emergency_beds": 15, "emergency_available": 4,
        "established_year": 2001,
        "departments": ["General Medicine", "Surgery", "Pediatrics", "Gynecology"],
        "amenities": ["Pharmacy", "Parking", "Ambulance", "Blood Bank"],
    },
    {
        "name": "Divine Multispeciality Hospital",
        "city": "Navi Mumbai", "state": "Maharashtra", "pincode": "400709",
        "address": "Sector 19, Ghansoli, Navi Mumbai",
        "latitude": "19.1206459", "longitude": "73.0028827",
        "phone": "022-27690000", "email": "divine@multispeciality.in",
        "website": "",
        "registration_number": "MH-NM-003",
        "description": "Affordable multi-speciality care with round-the-clock emergency services.",
        "total_beds": 150, "available_beds": 45,
        "icu_total": 15, "icu_available": 4,
        "emergency_beds": 10, "emergency_available": 3,
        "established_year": 2010,
        "departments": ["General Medicine", "Orthopedics", "Dermatology", "ENT"],
        "amenities": ["Pharmacy", "Parking", "Cafeteria"],
    },
    {
        "name": "Indravati Hospital",
        "city": "Navi Mumbai", "state": "Maharashtra", "pincode": "400701",
        "address": "Ghansoli, Navi Mumbai",
        "latitude": "19.1257745", "longitude": "73.0010508",
        "phone": "022-27694444", "email": "indravati@hospital.in",
        "website": "",
        "registration_number": "MH-NM-004",
        "description": "Community hospital focused on primary and secondary care.",
        "total_beds": 100, "available_beds": 30,
        "icu_total": 10, "icu_available": 2,
        "emergency_beds": 8, "emergency_available": 2,
        "established_year": 2005,
        "departments": ["General Medicine", "Surgery", "Pediatrics"],
        "amenities": ["Pharmacy", "Parking"],
    },
    {
        "name": "Frisson Multispeciality Hospital",
        "city": "Navi Mumbai", "state": "Maharashtra", "pincode": "400709",
        "address": "Ghansoli, Navi Mumbai",
        "latitude": "19.1189673", "longitude": "73.0032700",
        "phone": "022-27698888", "email": "frisson@hospital.in",
        "website": "",
        "registration_number": "MH-NM-005",
        "description": "Modern multi-speciality facility with advanced diagnostic services.",
        "total_beds": 120, "available_beds": 35,
        "icu_total": 12, "icu_available": 3,
        "emergency_beds": 8, "emergency_available": 2,
        "established_year": 2013,
        "departments": ["Cardiology", "Pulmonology", "Neurology", "Surgery"],
        "amenities": ["Pharmacy", "Parking", "ATM", "Ambulance"],
    },
    # ── Thane ─────────────────────────────────────────────────────────────
    {
        "name": "Jupiter Hospital",
        "city": "Thane", "state": "Maharashtra", "pincode": "400601",
        "address": "Eastern Express Highway, Thane West",
        "latitude": "19.2010000", "longitude": "72.9780000",
        "phone": "022-21826767", "email": "info@jupiterhospital.com",
        "website": "https://www.jupiterhospital.com",
        "registration_number": "MH-TH-001",
        "description": "One of the largest private hospitals in Thane with 375+ beds.",
        "total_beds": 375, "available_beds": 100,
        "icu_total": 40, "icu_available": 10,
        "emergency_beds": 25, "emergency_available": 6,
        "established_year": 2006,
        "departments": ["Cardiology", "Neurology", "Oncology", "Transplant", "Orthopedics"],
        "amenities": ["Pharmacy", "Cafeteria", "Parking", "ATM", "Blood Bank", "Ambulance", "Chapel"],
    },
    {
        "name": "Bethany Hospital",
        "city": "Thane", "state": "Maharashtra", "pincode": "400601",
        "address": "Bethany Hospital Road, Thane West",
        "latitude": "19.1947000", "longitude": "72.9718000",
        "phone": "022-25340600", "email": "info@bethanyhospital.in",
        "website": "https://www.bethanyhospital.in",
        "registration_number": "MH-TH-002",
        "description": "Missionary hospital with a legacy of compassionate care since 1945.",
        "total_beds": 250, "available_beds": 70,
        "icu_total": 25, "icu_available": 7,
        "emergency_beds": 20, "emergency_available": 5,
        "established_year": 1945,
        "departments": ["General Medicine", "Surgery", "Gynecology", "Pediatrics", "Psychiatry"],
        "amenities": ["Pharmacy", "Cafeteria", "Parking", "Chapel", "Blood Bank"],
    },
    {
        "name": "Hiranandani Hospital",
        "city": "Thane", "state": "Maharashtra", "pincode": "400607",
        "address": "Hiranandani Estate, Thane",
        "latitude": "19.2594000", "longitude": "72.9781000",
        "phone": "022-25773000", "email": "info@hiranandanihospital.com",
        "website": "https://www.hiranandanihospital.com",
        "registration_number": "MH-TH-003",
        "description": "Premium super-speciality hospital in Hiranandani Estate township.",
        "total_beds": 300, "available_beds": 85,
        "icu_total": 30, "icu_available": 8,
        "emergency_beds": 20, "emergency_available": 5,
        "established_year": 2004,
        "departments": ["Cardiology", "Neurology", "Gastroenterology", "Urology", "Dermatology"],
        "amenities": ["Pharmacy", "Cafeteria", "Parking", "ATM", "Blood Bank", "Ambulance"],
    },
    {
        "name": "Currae Specialty Hospital",
        "city": "Thane", "state": "Maharashtra", "pincode": "400601",
        "address": "Wagle Estate, Thane West",
        "latitude": "19.1865000", "longitude": "72.9755000",
        "phone": "022-25820000", "email": "info@curraehospital.com",
        "website": "https://www.curraehospital.com",
        "registration_number": "MH-TH-004",
        "description": "Specialty hospital known for maternity, fertility, and women's health.",
        "total_beds": 180, "available_beds": 50,
        "icu_total": 18, "icu_available": 4,
        "emergency_beds": 12, "emergency_available": 3,
        "established_year": 2012,
        "departments": ["Gynecology", "Pediatrics", "General Medicine", "Orthopedics"],
        "amenities": ["Pharmacy", "Parking", "Cafeteria", "Ambulance"],
    },
    # ── Dombivli ──────────────────────────────────────────────────────────
    {
        "name": "SRV Hospitals - Dombivli",
        "city": "Dombivli", "state": "Maharashtra", "pincode": "421201",
        "address": "Dombivli East, Thane District",
        "latitude": "19.2073183", "longitude": "73.1043121",
        "phone": "0251-2870000", "email": "dombivli@srvhospitals.com",
        "website": "https://www.srvhospitals.com",
        "registration_number": "MH-DOM-001",
        "description": "Leading multispeciality hospital in Dombivli with 24x7 emergency care.",
        "total_beds": 200, "available_beds": 55,
        "icu_total": 20, "icu_available": 5,
        "emergency_beds": 15, "emergency_available": 4,
        "established_year": 2008,
        "departments": ["Cardiology", "Orthopedics", "Neurology", "Surgery", "Pediatrics"],
        "amenities": ["Pharmacy", "Parking", "Cafeteria", "Ambulance", "Blood Bank"],
    },
    {
        "name": "AIMS Hospital",
        "city": "Dombivli", "state": "Maharashtra", "pincode": "421201",
        "address": "Dombivli East, Thane District",
        "latitude": "19.2160000", "longitude": "73.0910000",
        "phone": "0251-2880000", "email": "info@aimshospital.in",
        "website": "",
        "registration_number": "MH-DOM-002",
        "description": "AIMS Hospital provides comprehensive healthcare to Dombivli residents.",
        "total_beds": 150, "available_beds": 40,
        "icu_total": 15, "icu_available": 4,
        "emergency_beds": 10, "emergency_available": 3,
        "established_year": 2007,
        "departments": ["General Medicine", "Surgery", "Gynecology", "ENT"],
        "amenities": ["Pharmacy", "Parking", "Ambulance"],
    },
    {
        "name": "ICON Hospital",
        "city": "Dombivli", "state": "Maharashtra", "pincode": "421201",
        "address": "Dombivli East, Thane District",
        "latitude": "19.2180000", "longitude": "73.0905000",
        "phone": "0251-2885000", "email": "info@iconhospital.in",
        "website": "",
        "registration_number": "MH-DOM-003",
        "description": "Trusted community hospital with specialised diagnostics.",
        "total_beds": 120, "available_beds": 35,
        "icu_total": 12, "icu_available": 3,
        "emergency_beds": 8, "emergency_available": 2,
        "established_year": 2011,
        "departments": ["General Medicine", "Orthopedics", "Dermatology"],
        "amenities": ["Pharmacy", "Parking"],
    },
    {
        "name": "Apex Hospital Dombivli",
        "city": "Dombivli", "state": "Maharashtra", "pincode": "421201",
        "address": "Dombivli West, Thane District",
        "latitude": "19.2145000", "longitude": "73.0855000",
        "phone": "0251-2890000", "email": "apexdombivli@hospital.in",
        "website": "",
        "registration_number": "MH-DOM-004",
        "description": "Apex Dombivli focuses on affordable secondary care.",
        "total_beds": 100, "available_beds": 28,
        "icu_total": 10, "icu_available": 2,
        "emergency_beds": 8, "emergency_available": 2,
        "established_year": 2009,
        "departments": ["General Medicine", "Surgery", "Pediatrics"],
        "amenities": ["Pharmacy", "Parking", "Ambulance"],
    },
    {
        "name": "Dandekar Hospital",
        "city": "Dombivli", "state": "Maharashtra", "pincode": "421201",
        "address": "Dombivli East, Thane District",
        "latitude": "19.2155400", "longitude": "73.0903400",
        "phone": "0251-2895000", "email": "dandekar@hospital.in",
        "website": "",
        "registration_number": "MH-DOM-005",
        "description": "Family-run hospital with decades of service to Dombivli community.",
        "total_beds": 80, "available_beds": 22,
        "icu_total": 8, "icu_available": 2,
        "emergency_beds": 5, "emergency_available": 1,
        "established_year": 1985,
        "departments": ["General Medicine", "Surgery", "Gynecology"],
        "amenities": ["Pharmacy", "Parking"],
    },
    # ── Mumbai (Major) ─────────────────────────────────────────────────────
    {
        "name": "Nanavati Max Super Speciality Hospital",
        "city": "Mumbai", "state": "Maharashtra", "pincode": "400056",
        "address": "SV Road, Vile Parle West, Mumbai",
        "latitude": "19.0958824", "longitude": "72.8402610",
        "phone": "022-26267500", "email": "info@nanavatihospital.org",
        "website": "https://www.nanavatimaxhospital.org",
        "registration_number": "MH-MUM-001",
        "description": "Premier super-speciality hospital with 350+ beds and NABH accreditation.",
        "total_beds": 350, "available_beds": 90,
        "icu_total": 45, "icu_available": 12,
        "emergency_beds": 30, "emergency_available": 8,
        "established_year": 1950,
        "departments": ["Cardiology", "Oncology", "Neurology", "Transplant", "Robotic Surgery"],
        "amenities": ["Pharmacy", "Cafeteria", "Parking", "ATM", "Blood Bank", "Ambulance", "Helipad"],
    },
    {
        "name": "Jaslok Hospital & Research Centre",
        "city": "Mumbai", "state": "Maharashtra", "pincode": "400026",
        "address": "15, Dr G Deshmukh Marg, Pedder Road, Mumbai",
        "latitude": "18.9716603", "longitude": "72.8098319",
        "phone": "022-66573333", "email": "info@jaslokhospital.net",
        "website": "https://www.jaslokhospital.net",
        "registration_number": "MH-MUM-002",
        "description": "Renowned quaternary care hospital known for complex surgeries since 1973.",
        "total_beds": 354, "available_beds": 95,
        "icu_total": 50, "icu_available": 14,
        "emergency_beds": 30, "emergency_available": 7,
        "established_year": 1973,
        "departments": ["Cardiology", "Neurosurgery", "Oncology", "Nephrology", "Transplant"],
        "amenities": ["Pharmacy", "Cafeteria", "Parking", "ATM", "Blood Bank", "Ambulance", "Helipad"],
    },
    {
        "name": "Wockhardt Hospitals Mumbai Central",
        "city": "Mumbai", "state": "Maharashtra", "pincode": "400011",
        "address": "1877, Dr Anandrao Nair Marg, Mumbai Central",
        "latitude": "18.9752117", "longitude": "72.8238875",
        "phone": "022-61784444", "email": "info@wockhardthospitals.com",
        "website": "https://www.wockhardthospitals.com",
        "registration_number": "MH-MUM-003",
        "description": "Multi-speciality tertiary care hospital with cutting-edge cardiac and neuro care.",
        "total_beds": 280, "available_beds": 75,
        "icu_total": 35, "icu_available": 9,
        "emergency_beds": 20, "emergency_available": 5,
        "established_year": 1989,
        "departments": ["Cardiology", "Neurology", "Orthopedics", "Gastroenterology", "Endocrinology"],
        "amenities": ["Pharmacy", "Cafeteria", "Parking", "ATM", "Blood Bank", "Ambulance"],
    },
    {
        "name": "Gleneagles Hospital Mumbai",
        "city": "Mumbai", "state": "Maharashtra", "pincode": "400093",
        "address": "35, S. R. Mehta Marg, Eastern Suburbs, Mumbai",
        "latitude": "18.9995043", "longitude": "72.8406054",
        "phone": "022-25219000", "email": "info@gleneagleshospitals.com",
        "website": "https://www.gleneagleshospitals.com/mumbai",
        "registration_number": "MH-MUM-004",
        "description": "JCI-accredited multi-speciality hospital part of the Gleneagles global network.",
        "total_beds": 400, "available_beds": 110,
        "icu_total": 55, "icu_available": 15,
        "emergency_beds": 35, "emergency_available": 9,
        "established_year": 1972,
        "departments": ["Transplant", "Oncology", "Cardiology", "Neurology", "Urology", "Pulmonology"],
        "amenities": ["Pharmacy", "Cafeteria", "Parking", "ATM", "Blood Bank", "Ambulance", "Helipad", "Wi-Fi"],
    },
    {
        "name": "Fortis SL Raheja Hospital",
        "city": "Mumbai", "state": "Maharashtra", "pincode": "400016",
        "address": "Raheja Rugnalaya Marg, Mahim West, Mumbai",
        "latitude": "19.0462883", "longitude": "72.8426504",
        "phone": "022-66529999", "email": "slraheja@fortishealthcare.com",
        "website": "https://www.fortishealthcare.com",
        "registration_number": "MH-MUM-005",
        "description": "Fortis flagship hospital with dedicated centres for cardiology and orthopaedics.",
        "total_beds": 280, "available_beds": 72,
        "icu_total": 35, "icu_available": 9,
        "emergency_beds": 22, "emergency_available": 5,
        "established_year": 1994,
        "departments": ["Cardiology", "Orthopedics", "Neurosciences", "Oncology", "Nephrology"],
        "amenities": ["Pharmacy", "Cafeteria", "Parking", "ATM", "Blood Bank", "Ambulance"],
    },
    {
        "name": "Zen Multispeciality Hospital Chembur",
        "city": "Mumbai", "state": "Maharashtra", "pincode": "400071",
        "address": "Plot No. 425, 10th Road, Chembur, Mumbai",
        "latitude": "19.0558779", "longitude": "72.8967920",
        "phone": "022-25218888", "email": "info@zenhospitals.com",
        "website": "https://www.zenhospitals.com",
        "registration_number": "MH-MUM-006",
        "description": "NABH-accredited hospital catering to Eastern Mumbai with advanced ICU.",
        "total_beds": 200, "available_beds": 55,
        "icu_total": 25, "icu_available": 6,
        "emergency_beds": 15, "emergency_available": 4,
        "established_year": 2002,
        "departments": ["General Medicine", "Cardiology", "Orthopedics", "Gynecology", "Surgery"],
        "amenities": ["Pharmacy", "Parking", "Cafeteria", "Ambulance", "Blood Bank"],
    },
    {
        "name": "CritiCare Asia Multi Specialty Hospital",
        "city": "Mumbai", "state": "Maharashtra", "pincode": "400057",
        "address": "Plot 52A, Juhu-Versova Link Road, Andheri West, Mumbai",
        "latitude": "19.0760723", "longitude": "72.8862077",
        "phone": "022-61415555", "email": "info@criticareasiahospitals.com",
        "website": "https://www.criticareasiahospitals.com",
        "registration_number": "MH-MUM-007",
        "description": "Tertiary care hospital known for its state-of-the-art ICU and trauma centre.",
        "total_beds": 220, "available_beds": 60,
        "icu_total": 30, "icu_available": 8,
        "emergency_beds": 18, "emergency_available": 4,
        "established_year": 2005,
        "departments": ["Critical Care", "Neurology", "Cardiology", "Pulmonology", "Gastroenterology"],
        "amenities": ["Pharmacy", "Parking", "Cafeteria", "ATM", "Blood Bank", "Ambulance"],
    },
    {
        "name": "Apex Superspeciality Hospital Borivali",
        "city": "Mumbai", "state": "Maharashtra", "pincode": "400092",
        "address": "S V Road, Borivali West, Mumbai",
        "latitude": "19.2293416", "longitude": "72.8466084",
        "phone": "022-28905555", "email": "borivali@apexhospitals.in",
        "website": "",
        "registration_number": "MH-MUM-008",
        "description": "Super-speciality hospital serving Western Mumbai suburbs.",
        "total_beds": 180, "available_beds": 50,
        "icu_total": 20, "icu_available": 5,
        "emergency_beds": 12, "emergency_available": 3,
        "established_year": 2003,
        "departments": ["Cardiology", "Orthopedics", "Neurology", "Surgery", "Urology"],
        "amenities": ["Pharmacy", "Parking", "Cafeteria", "ATM", "Ambulance"],
    },
    {
        "name": "Prince Aly Khan Hospital",
        "city": "Mumbai", "state": "Maharashtra", "pincode": "400010",
        "address": "Aly Khan Road, Mazagaon, Mumbai",
        "latitude": "18.9779000", "longitude": "72.8345000",
        "phone": "022-23773800", "email": "info@pakhhospital.com",
        "website": "https://www.pakhhospital.com",
        "registration_number": "MH-MUM-009",
        "description": "Historic municipal-grade hospital providing affordable tertiary care since 1951.",
        "total_beds": 320, "available_beds": 90,
        "icu_total": 40, "icu_available": 10,
        "emergency_beds": 25, "emergency_available": 6,
        "established_year": 1951,
        "departments": ["General Medicine", "Surgery", "Obstetrics", "Pediatrics", "Orthopedics"],
        "amenities": ["Pharmacy", "Parking", "Blood Bank", "Ambulance"],
    },
    {
        "name": "Kokilaben Dhirubhai Ambani Hospital (Andheri)",
        "city": "Mumbai", "state": "Maharashtra", "pincode": "400053",
        "address": "Rao Saheb Achutrao Patwardhan Marg, Four Bungalows, Andheri West, Mumbai",
        "latitude": "19.1300000", "longitude": "72.8259000",
        "phone": "022-30999999", "email": "info@kokilabenhospital.com",
        "website": "https://www.kokilabenhospital.com",
        "registration_number": "MH-MUM-010",
        "description": "Flagship quaternary care hospital with 750 beds and India's first da Vinci robotic surgery.",
        "total_beds": 750, "available_beds": 200,
        "icu_total": 85, "icu_available": 22,
        "emergency_beds": 50, "emergency_available": 12,
        "established_year": 2009,
        "departments": ["Cardiology", "Neurology", "Oncology", "Transplant", "Robotic Surgery", "Pediatric ICU"],
        "amenities": ["Pharmacy", "Cafeteria", "Parking", "ATM", "Blood Bank", "Ambulance", "Helipad", "Wi-Fi", "Prayer Room"],
    },
]

# ─────────────────────────────────────────────
# 2.  HELPER — get or create a User for a hospital
# ─────────────────────────────────────────────

def get_or_create_hospital_user(hospital_name, email):
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "full_name": hospital_name,
            "role": User.Role.HOSPITAL,
            "approval_status": User.ApprovalStatus.APPROVED,
            "phone": "",
            "is_active": True,
            "is_staff": False,
        }
    )
    if created:
        user.set_password("Hospital@12345")
        user.save()
        print(f"  ✔ Created user: {email}")
    else:
        print(f"  ↺ User already exists: {email}")
    return user


# ─────────────────────────────────────────────
# 3.  SEED
# ─────────────────────────────────────────────

from hospital_service.models import Hospital, Department, Amenity  # adjust import path if needed

created_count = 0
skipped_count = 0

for data in HOSPITALS_DATA:
    reg = data["registration_number"]

    if Hospital.objects.filter(registration_number=reg).exists():
        print(f"⚠  Hospital already exists ({reg}), skipping.")
        skipped_count += 1
        continue

    # derive a unique email for the hospital user
    slug = reg.lower().replace("-", "")
    email = data.get("email") or f"{slug}@hospital.in"
    # make sure email is unique as a user login
    user_email = f"admin.{slug}@hospital.in"

    user = get_or_create_hospital_user(data["name"], user_email)

    hospital = Hospital.objects.create(
        user=user,
        name=data["name"],
        registration_number=reg,
        description=data["description"],
        address=data["address"],
        city=data["city"],
        state=data["state"],
        pincode=data["pincode"],
        latitude=Decimal(data["latitude"]),
        longitude=Decimal(data["longitude"]),
        phone=data["phone"],
        email=email,
        website=data.get("website", ""),
        total_beds=data["total_beds"],
        available_beds=data["available_beds"],
        icu_total=data["icu_total"],
        icu_available=data["icu_available"],
        emergency_beds=data["emergency_beds"],
        emergency_available=data["emergency_available"],
        status=Hospital.Status.ACTIVE,
        is_verified=True,
        established_year=data.get("established_year"),
        logo_url="",
        image_url="",
    )

    # Departments
    for dept_name in data.get("departments", []):
        Department.objects.create(
            hospital=hospital,
            name=dept_name,
            is_active=True,
        )

    # Amenities
    for amenity_name in data.get("amenities", []):
        Amenity.objects.create(
            hospital=hospital,
            name=amenity_name,
            is_available=True,
        )

    print(f"✅ Created: {hospital.name} ({hospital.city})")
    created_count += 1

print(f"\n── Done ──────────────────────────────────────")
print(f"  Created : {created_count}")
print(f"  Skipped : {skipped_count}")
print(f"  Total   : {len(HOSPITALS_DATA)}")