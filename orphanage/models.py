from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
import os
from django.conf import settings

# Custom User Model (Extending Django's User System)
class User(AbstractUser):
    dob = models.DateField(null=True)
    age = models.IntegerField(null=True, blank=True)
    place = models.CharField(max_length=255,null=True)
    aadhaar_number = models.CharField(max_length=12, unique=True,null=True)

    def save(self, *args, **kwargs):
        if self.dob:
            self.age = date.today().year - self.dob.year
        else:
            self.age = None
        super().save(*args, **kwargs)

# Child Model
class Child(models.Model):
    STATUS_CHOICES = [('Adopted', 'Adopted'), ('Not Adopted', 'Not Adopted')]

    name = models.CharField(max_length=255)
    dob = models.DateField()
    age = models.IntegerField(null=True, blank=True)
    photo = models.ImageField(upload_to='child_photos/')
    additional_photos = models.JSONField(default=list)  # Stores multiple image URLs
    health_status = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Not Adopted')
    caretaker = models.ForeignKey('Caretaker', on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.dob:
            self.age = date.today().year - self.dob.year
        
        # Ensure full paths are stored for additional photos
        self.additional_photos = [
            os.path.join(settings.MEDIA_URL, photo) for photo in self.additional_photos
        ]

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# Caretaker Model
class Caretaker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Link to User model
    name = models.CharField(max_length=255)
    dob = models.DateField()
    age = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=15)
    experience = models.IntegerField()
    aadhaar_number = models.CharField(max_length=12, unique=True)
    place = models.CharField(max_length=255)
    education = models.CharField(max_length=255)
    marital_status = models.CharField(max_length=15, choices=[('Single', 'Single'), ('Married', 'Married')])
    id_proof = models.FileField(upload_to='caretaker_id_proofs/')
    experience_certificate = models.FileField(upload_to='caretaker_experience_certificates/')
    status = models.CharField(max_length=15, choices=[('Approved', 'Approved'), ('Not Approved', 'Not Approved')], default='Approved')
    assigned_children = models.JSONField(default=list)

    def save(self, *args, **kwargs):
        if self.dob:
            self.age = date.today().year - self.dob.year
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# Timetable Model (Common for all children)
class TimeTable(models.Model):
    caretaker = models.ForeignKey('Caretaker', on_delete=models.CASCADE)
    week_start_date = models.DateField()  # Start of the week (Monday)
    
    # Time slots
    MORNING = 'Morning'
    AFTERNOON = 'Afternoon'
    EVENING = 'Evening'
    NIGHT = 'Night'
    
    TIME_SLOTS = [
        (MORNING, 'Morning'),
        (AFTERNOON, 'Afternoon'),
        (EVENING, 'Evening'),
        (NIGHT, 'Night'),
    ]

    time_slot = models.CharField(max_length=20, choices=TIME_SLOTS)
    monday = models.TextField(default="", blank=True)
    tuesday = models.TextField(default="", blank=True)
    wednesday = models.TextField(default="", blank=True)
    thursday = models.TextField(default="", blank=True)
    friday = models.TextField(default="", blank=True)
    saturday = models.TextField(default="", blank=True)
    sunday = models.TextField(default="", blank=True)

    def __str__(self):
        return f"Timetable ({self.week_start_date}) - {self.time_slot}"

# Diet Plan Model (Common for all children)
class DietPlan(models.Model):
    caretaker = models.ForeignKey('Caretaker', on_delete=models.CASCADE)
    week_start_date = models.DateField()  # Start of the week (Monday)

    time_slot = models.CharField(max_length=20, choices=TimeTable.TIME_SLOTS)
    monday = models.CharField(max_length=255, default="", blank=True)
    tuesday = models.CharField(max_length=255, default="", blank=True)
    wednesday = models.CharField(max_length=255, default="", blank=True)
    thursday = models.CharField(max_length=255, default="", blank=True)
    friday = models.CharField(max_length=255, default="", blank=True)
    saturday = models.CharField(max_length=255, default="", blank=True)
    sunday = models.CharField(max_length=255, default="", blank=True)

    def __str__(self):
        return f"Diet Plan ({self.week_start_date}) - {self.time_slot}"

# Donations Model
class Donation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"

# Adoption Request Model
class AdoptionRequest(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')]

    name = models.CharField(max_length=255)
    dob = models.DateField()
    age = models.IntegerField(null=True, blank=True)
    family_members = models.IntegerField()
    reason = models.TextField()
    annual_income = models.DecimalField(max_digits=10, decimal_places=2)
    job_name = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    aadhaar_number = models.CharField(max_length=12, unique=True)
    phone_number = models.CharField(max_length=15)
    email_id = models.EmailField()
    id_proof = models.FileField(upload_to='adoption_id_proofs/')
    income_certificate = models.FileField(upload_to='adoption_income_certificates/')
    salary_certificate = models.FileField(upload_to='adoption_salary_certificates/', blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')

    # New Fields for Child Info
    child_id = models.IntegerField()
    child_name = models.CharField(max_length=255)
    child_age = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.dob:
            self.age = date.today().year - self.dob.year
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.child_name} ({self.status})"


from datetime import datetime

class Report(models.Model):
    caretaker_name = models.CharField(max_length=255)  # Store caretaker's name as a string
    child_name = models.CharField(max_length=255)  # Store child's name as a string
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)




class Feedback(models.Model):
    name = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class Details(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    location = models.CharField(max_length=255)
    map_link = models.URLField()

    photo1 = models.ImageField(upload_to='details/')
    photo2 = models.ImageField(upload_to='details/')

    def __str__(self):
        return self.name


class AdoptedChild(models.Model):
    name = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    health_status = models.TextField()
    date_deleted = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name