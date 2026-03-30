from django.db import models


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
    department = models.ForeignKey(Department,on_delete=models.CASCADE   # important decision (explained below)
)
    subdepartment = models.ForeignKey(SubDepartment,on_delete=models.CASCADE
    )
    email = models.EmailField(unique=True, null=True, blank=True)
    skills = models.TextField()

    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    experience = models.IntegerField(default=0)
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