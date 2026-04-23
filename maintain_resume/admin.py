from django.contrib import admin
from .models import Department, SubDepartment, Resume, PasswordResetOTP



admin.site.site_header = "Resume Management Admin"
admin.site.site_title = "Resume Management Admin Portal"    
admin.site.index_title = "Welcome to the Resume Management Admin Portal"    
admin.site.register(Department)
admin.site.register(SubDepartment)
admin.site.register(Resume)
admin.site.register(PasswordResetOTP)

