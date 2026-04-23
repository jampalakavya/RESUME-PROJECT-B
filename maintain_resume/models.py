from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name
    
class SubDepartment(models.Model):
    department = models.ForeignKey(Department,on_delete=models.CASCADE,related_name='subdepartments')
    name = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.department.name} - {self.name}"

class Resume(models.Model):
    user = models.ForeignKey(
    User, 
    on_delete=models.CASCADE, 
    related_name='resumes',
    null=True,   
    blank=True
)
    department = models.ForeignKey(Department,on_delete=models.CASCADE 
)
    subdepartment = models.ForeignKey(SubDepartment,on_delete=models.CASCADE
    )
    email = models.EmailField(unique=True, null=True, blank=True)
    skills = models.TextField()

    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    experience = models.IntegerField(default=0)
    is_bookmarked=models.BooleanField(default=False)
    def __str__(self):
        return self.name
    
from django.db import models
from django.contrib.auth.models import User

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email
    
class ResumeTemplate(models.Model):
    name = models.CharField(max_length=100)
    preview_image = models.ImageField(upload_to='templates/', null=True, blank=True)

    def __str__(self):
        return self.name
    
    
    
# models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserResume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_resumes')

    title = models.CharField(max_length=200)

    # Personal
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=255, blank=True)

    # Links
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    portfolio = models.URLField(blank=True)

    summary = models.TextField(blank=True)
    interests = models.TextField(blank=True)

    template_name = models.CharField(max_length=100)

    file = models.FileField(upload_to='generated_resumes/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


class Education(models.Model):
    resume = models.ForeignKey(UserResume, on_delete=models.CASCADE, related_name='educations')
    degree = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    year = models.CharField(max_length=50, blank=True)


class Experience(models.Model):
    resume = models.ForeignKey(UserResume, on_delete=models.CASCADE, related_name='experiences')
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    description = models.TextField(blank=True)


class Project(models.Model):
    resume = models.ForeignKey(UserResume, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)


class Skill(models.Model):
    resume = models.ForeignKey(UserResume, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)


class Certification(models.Model):
    resume = models.ForeignKey(UserResume, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=255)


class Achievement(models.Model):
    resume = models.ForeignKey(UserResume, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=255)


class Language(models.Model):
    resume = models.ForeignKey(UserResume, on_delete=models.CASCADE, related_name='languages')
    name = models.CharField(max_length=100)