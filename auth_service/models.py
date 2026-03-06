from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models





class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('approval_status', 'approved')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        USER     = 'user',     'Patient'
        DOCTOR   = 'doctor',   'Doctor'
        HOSPITAL = 'hospital', 'Hospital'
        ADMIN    = 'admin',    'Admin'

    class ApprovalStatus(models.TextChoices):
        PENDING  = 'pending',  'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    email            = models.EmailField(unique=True)
    full_name        = models.CharField(max_length=255)
    role             = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    phone            = models.CharField(max_length=20, blank=True)
    approval_status  = models.CharField(max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.APPROVED)
    profile_picture  = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active        = models.BooleanField(default=True)
    is_staff         = models.BooleanField(default=False)
    date_joined      = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.email} ({self.role})'

    def save(self, *args, **kwargs):
        # Doctors and hospitals need approval
        if self.role in [self.Role.DOCTOR, self.Role.HOSPITAL] and not self.pk:
            self.approval_status = self.ApprovalStatus.PENDING
        super().save(*args, **kwargs)


