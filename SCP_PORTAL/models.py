from django.db import models
from django.contrib.auth.models import User

# This model adds a 'role' field to Django's built-in User
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_staff_admin = models.BooleanField(default=False)  # 👈 New field
    def __str__(self):
        return f"{self.user.username} - {self.role}"
    



# Student Personal Information Model 


# models.py
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10)
    contact = models.CharField(max_length=15)

    # 10th Grade Details
    school_10      = models.CharField(max_length=255, blank=True)
    tenth_board    = models.CharField(max_length=100, null=True, blank=True)
    year_10 = models.IntegerField(null=True, blank=True)
    maths_10 = models.IntegerField(null=True, blank=True)
    science_10 = models.IntegerField(null=True, blank=True)
    english_10 = models.IntegerField(null=True, blank=True)
    social_10 = models.IntegerField(null=True, blank=True)
    tenth_percentage = models.FloatField(null=True, blank=True)

    # 12th Grade Details
    school_12       = models.CharField(max_length=255, blank=True)
    twelfth_board   = models.CharField(max_length=100, null=True, blank=True)
    twelfth_stream  = models.CharField(max_length=50, null=True, blank=True)
    year_12 = models.IntegerField(null=True, blank=True)
    physics_12 = models.IntegerField(null=True, blank=True)
    chemistry_12 = models.IntegerField(null=True, blank=True)
    maths_12 = models.IntegerField(null=True, blank=True)
    english_12 = models.IntegerField(null=True, blank=True)
    twelfth_percentage = models.FloatField(null=True, blank=True)

    # Choice Filling
    choice_1 = models.CharField(max_length=100, default="")
    choice_2 = models.CharField(max_length=100, default="")
    choice_3 = models.CharField(max_length=100, default="")

    # Seat Allocation Status
    allocated_branch = models.CharField(max_length=100, null=True, blank=True)
    branch_accepted = models.BooleanField(default=False)

    # Payment
    payment_verified = models.BooleanField(default=False)
    receipt = models.FileField(upload_to='receipts/', null=True, blank=True)  # NEW

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"

    def calculate_percentages(self):
        # Use 'is not None' so zeros count as valid marks
        tenth_scores = [x for x in [self.maths_10, self.science_10, self.english_10, self.social_10] if x is not None]
        self.tenth_percentage = sum(tenth_scores) / len(tenth_scores) if tenth_scores else None

        twelfth_scores = [x for x in [self.physics_12, self.chemistry_12, self.maths_12, self.english_12] if x is not None]
        self.twelfth_percentage = sum(twelfth_scores) / len(twelfth_scores) if twelfth_scores else None