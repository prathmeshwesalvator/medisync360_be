from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class DoctorProfile(models.Model):
    SPEC=[("general","General Physician"),("cardiology","Cardiology"),("neurology","Neurology"),("orthopedics","Orthopedics"),("pediatrics","Pediatrics"),("gynecology","Gynecology"),("dermatology","Dermatology"),("ophthalmology","Ophthalmology"),("ent","ENT"),("psychiatry","Psychiatry"),("oncology","Oncology"),("surgery","Surgery"),("dentistry","Dentistry"),("gastroenterology","Gastroenterology"),("pulmonology","Pulmonology"),("endocrinology","Endocrinology"),("urology","Urology"),("nephrology","Nephrology")]
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="doctor_profile")
    hospital=models.ForeignKey("hospital_service.Hospital",on_delete=models.SET_NULL,null=True,blank=True,related_name="doctors")
    specialization=models.CharField(max_length=50,choices=SPEC)
    qualification=models.CharField(max_length=300)
    experience_years=models.PositiveIntegerField(default=0)
    license_number=models.CharField(max_length=100,unique=True)
    bio=models.TextField(blank=True)
    languages=models.CharField(max_length=200,blank=True)
    consultation_fee=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    rating=models.DecimalField(max_digits=3,decimal_places=2,default=0.0)
    total_reviews=models.PositiveIntegerField(default=0)
    is_available_today=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        db_table="doctor_profiles"
    def __str__(self):
        return f"Dr. {self.user.full_name}"

class WeeklySchedule(models.Model):
    DAYS=[(0,"Monday"),(1,"Tuesday"),(2,"Wednesday"),(3,"Thursday"),(4,"Friday"),(5,"Saturday"),(6,"Sunday")]
    doctor=models.ForeignKey(DoctorProfile,on_delete=models.CASCADE,related_name="weekly_schedule")
    day_of_week=models.IntegerField(choices=DAYS)
    start_time=models.TimeField()
    end_time=models.TimeField()
    slot_duration_minutes=models.PositiveIntegerField(default=30)
    max_patients=models.PositiveIntegerField(default=20)
    is_active=models.BooleanField(default=True)
    class Meta:
        db_table="weekly_schedules"
        unique_together=["doctor","day_of_week"]
        ordering=["day_of_week","start_time"]

class SlotBlock(models.Model):
    doctor=models.ForeignKey(DoctorProfile,on_delete=models.CASCADE,related_name="slot_blocks")
    date=models.DateField()
    reason=models.CharField(max_length=200,blank=True)
    class Meta:
        db_table="slot_blocks"
        unique_together=["doctor","date"]

class TimeSlot(models.Model):
    STATUS=[("available","Available"),("booked","Booked"),("blocked","Blocked")]
    doctor=models.ForeignKey(DoctorProfile,on_delete=models.CASCADE,related_name="time_slots")
    date=models.DateField()
    start_time=models.TimeField()
    end_time=models.TimeField()
    status=models.CharField(max_length=20,choices=STATUS,default="available")
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table="time_slots"
        unique_together=["doctor","date","start_time"]
        ordering=["date","start_time"]

class DoctorReview(models.Model):
    doctor=models.ForeignKey(DoctorProfile,on_delete=models.CASCADE,related_name="reviews")
    patient=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="doctor_reviews")
    rating=models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    comment=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table="doctor_reviews"
        unique_together=["doctor","patient"]
    def save(self,*a,**kw):
        super().save(*a,**kw)
        from django.db.models import Avg
        agg=DoctorReview.objects.filter(doctor=self.doctor).aggregate(avg=Avg("rating"))
        self.doctor.rating=round(agg["avg"] or 0,2)
        self.doctor.total_reviews=DoctorReview.objects.filter(doctor=self.doctor).count()
        self.doctor.save(update_fields=["rating","total_reviews"])