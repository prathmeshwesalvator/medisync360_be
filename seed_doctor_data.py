import random
from decimal import Decimal
from datetime import time

from django.contrib.auth import get_user_model
from doctors_service.models import DoctorProfile, WeeklySchedule
from hospital_service.models import Hospital

User = get_user_model()


DOCTOR_NAMES = [
    "Aarav Mehta",
    "Priya Sharma",
    "Rohan Kulkarni",
    "Neha Patil",
    "Vikram Joshi",
    "Sneha Deshmukh",
    "Aditya Nair",
    "Kavya Iyer",
    "Rahul Verma",
    "Meera Kapoor",
    "Siddharth Shah",
    "Ananya Rao",
    "Arjun Malhotra",
    "Pooja Chavan",
    "Kunal Bhatia",
    "Ritika Jain",
    "Manish Gupta",
    "Tanvi Desai",
    "Harsh Vora",
    "Nikita Reddy",
]

QUALIFICATIONS = [
    "MBBS, MD",
    "MBBS, MS",
    "MBBS, DNB",
    "MBBS, MD, DM",
    "MBBS, MS, MCh",
]

LANGUAGES = [
    "English,Hindi",
    "English,Hindi,Marathi",
    "English,Hindi,Gujarati",
    "English,Marathi",
]

BIOS = [
    "Experienced specialist focused on patient-centered care.",
    "Dedicated doctor with extensive clinical expertise.",
    "Committed to evidence-based treatment and compassionate care.",
    "Specialist with modern diagnostic and treatment approach.",
]


hospitals = list(Hospital.objects.all())

if not hospitals:
    print("❌ No hospitals found. Seed hospitals first.")
    raise SystemExit()


specializations = [choice[0] for choice in DoctorProfile.SPEC]

created_count = 0
skipped_count = 0


for i, name in enumerate(DOCTOR_NAMES, start=1):
    email = f"doctor{i}@medisync.com"

    if User.objects.filter(email=email).exists():
        print(f"⚠ Doctor already exists: {email}")
        skipped_count += 1
        continue

    user = User.objects.create_user(
        email=email,
        password="Doctor@12345",
        full_name=name,
        role=User.Role.DOCTOR,
        phone=f"9876543{i:03d}",
        approval_status=User.ApprovalStatus.APPROVED,
    )

    doctor = DoctorProfile.objects.create(
        user=user,
        hospital=random.choice(hospitals),
        specialization=random.choice(specializations),
        qualification=random.choice(QUALIFICATIONS),
        experience_years=random.randint(1, 20),
        license_number=f"LIC-DOC-{10000+i}",
        bio=random.choice(BIOS),
        languages=random.choice(LANGUAGES),
        consultation_fee=Decimal(random.choice([500, 700, 1000, 1200, 1500])),
        rating=round(random.uniform(3.5, 5.0), 2),
        total_reviews=random.randint(5, 250),
        is_available_today=random.choice([True, False]),
    )

    for day in range(6):  # Monday-Saturday
        WeeklySchedule.objects.create(
            doctor=doctor,
            day_of_week=day,
            start_time=time(10, 0),
            end_time=time(18, 0),
            slot_duration_minutes=30,
            max_patients=20,
            is_active=True,
        )

    print(f"✅ Created Doctor: {name} → {doctor.hospital.name}")
    created_count += 1


print("\n── Done ─────────────────────────")
print(f"Created : {created_count}")
print(f"Skipped : {skipped_count}")
print(f"Total   : {len(DOCTOR_NAMES)}")