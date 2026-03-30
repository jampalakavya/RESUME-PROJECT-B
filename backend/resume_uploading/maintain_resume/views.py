from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Resume
from .serializers import *
from django.http import FileResponse, Http404
from django.db import transaction
from .models import Resume, Department, SubDepartment,PasswordResetOTP,User
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Count
from django.utils.timezone import now

from django.shortcuts import render
import re

from .utils import send_email
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random
from rest_framework import status



class RegisterView(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            #  Send Email (non-blocking)
            send_email(
                subject="Welcome to Resume Management System",
                # message=f"<h3>Hello {user.username}, welcome! </h3>",
                message = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account Confirmation</title>
</head>
<body style="margin:0; padding:0; background-color:#f1f5f9; font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color:#334155;">

<table width="100%" border="0" cellpadding="0" cellspacing="0" style="background-color:#f1f5f9; padding:40px 10px;">
    <tr>
        <td align="center">
            <!-- Main Email Container -->
            <table width="600" border="0" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.05); border:1px solid #e2e8f0;">
                
                <!-- Brand Header -->
                <tr>
                    <td style="padding:40px 40px 20px 40px;">
                        <h2 style="margin:0; color:#0f172a; font-size:20px; font-weight:800; text-transform:uppercase; letter-spacing:1.5px;">
                            <span style="background-color:#2563eb; color:#ffffff; padding:4px 8px; border-radius:4px;">RESUME</span> MANAGEMENT
                        </h2>
                    </td>
                </tr>

                <!-- Greeting & Heading -->
                <tr>
                    <td style="padding:20px 40px 10px 40px;">
                        <h1 style="margin:0; font-size:26px; font-weight:700; color:#1e293b; line-height:1.2;">
                            Registration Successful
                        </h1>
                    </td>
                </tr>

                <!-- Body Content -->
                <tr>
                    <td style="padding:20px 40px 30px 40px; font-size:16px; line-height:1.6; color:#475569;">
                        <p style="margin-top:0;">
                            Hello <strong>{user.first_name or user.username}</strong>,
                        </p>
                            We are pleased to confirm that your account associated with <strong>{user.email}</strong> has been successfully created within the Resume Management System.
                        </p>
                        <p>
                            You now have full access to our professional tools designed to streamline your document management, candidate tracking, and search operations.
                        </p>
                        
                        <!-- Formal Info Box -->
                        <div style="background-color:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:20px; margin:25px 0;">
                            <table width="100%" border="0" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="font-size:13px; color:#64748b; text-transform:uppercase; letter-spacing:0.5px; padding-bottom:5px;">Account Identifier</td>
                                </tr>
                                <tr>
                                    <td style="font-size:16px; font-weight:600; color:#0f172a;">{user.email}</td>
                                </tr>
                            </table>
                        </div>
                    </td>
                </tr>

                <!-- Security Footer -->
                <tr>
                    <td style="padding:0 40px 40px 40px; font-size:13px; color:#94a3b8; line-height:1.5;">
                        <hr style="border:none; border-top:1px solid #f1f5f9; margin-bottom:20px;">
                        <strong>Security Note:</strong> If you did not initiate this registration, please notify our administrative support team immediately at <a href="mailto:support@yourdomain.com" style="color:#2563eb; text-decoration:none;">support@yourdomain.com</a>.
                    </td>
                </tr>

                <!-- Legal Footer -->
                <tr>
                    <td style="background-color:#f8fafc; padding:30px 40px; text-align:center; font-size:12px; color:#64748b; border-top:1px solid #e2e8f0;">
                        &copy; 2026 Resume Management System. All rights reserved.<br>
                        Confidentiality Notice: This email and any attachments are intended solely for the addressee.
                    </td>
                </tr>

            </table>
        </td>
    </tr>
</table>

</body>
</html>
""",
                to_email=user.email
            )

            return Response({"msg": "User created"}, status=201)

        return Response(serializer.errors, status=400)
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import authenticate, get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        # 🔥 allow email login also
        user_obj = User.objects.filter(email=username).first()
        if user_obj:
            username = user_obj.username

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            })

        return Response({"error": "Invalid credentials"}, status=401)


User = get_user_model()

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=400)

        users = User.objects.filter(email=email)

        if not users.exists():
            return Response({"error": "User with this email does not exist"}, status=404)

        # if duplicates exist, take latest one
        user = users.order_by("-id").first()

        otp = str(random.randint(100000, 999999))

        # Delete old OTP if exists
        PasswordResetOTP.objects.filter(user=user).delete()

        # Save new OTP
        PasswordResetOTP.objects.create(user=user, otp=otp)

       
        try:
            send_email(
                subject="Password Reset OTP",
                message=f"""
                <h3>Hello {user.first_name or user.username},</h3>
                <p>Your password reset OTP is:</p>
                <h2>{otp}</h2>
            """,
                to_email=user.email
                )
            print("✅ Email sent")
        except Exception as e:
            print(" Email failed:", str(e))
            return Response({"error": str(e)}, status=500)



class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")

        if not email or not otp or not new_password:
            return Response({"error": "Email, OTP, and new password are required"}, status=400)

        users = User.objects.filter(email=email)

        if not users.exists():
            return Response({"error": "Invalid email"}, status=404)

        # take latest user
        user = users.order_by("-id").first()

        try:
            otp_record = PasswordResetOTP.objects.get(user=user, otp=otp)
        except PasswordResetOTP.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=400)

        # OTP expiry (10 min)
        if timezone.now() > otp_record.created_at + timedelta(minutes=10):
            otp_record.delete()
            return Response({"error": "OTP expired"}, status=400)

        # password validation
        if len(new_password) < 8:
            return Response({"error": "Password must be at least 8 characters"}, status=400)

        if not re.search(r"[A-Z]", new_password):
            return Response({"error": "Must contain uppercase letter"}, status=400)

        if not re.search(r"[a-z]", new_password):
            return Response({"error": "Must contain lowercase letter"}, status=400)

        if not re.search(r"[0-9]", new_password):
            return Response({"error": "Must contain number"}, status=400)

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", new_password):
            return Response({"error": "Must contain special character"}, status=400)

        user.set_password(new_password)
        user.save()

        otp_record.delete()

        return Response({"msg": "Password reset successful"}, status=200)

class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        #  Total resumes
        total_resumes = Resume.objects.count()

        #  Recent uploads (last 7 days)
        last_7_days = now() - timedelta(days=7)
        recent_uploads = Resume.objects.filter(
            uploaded_at__gte=last_7_days
        ).count()

        #  Department-wise count
        dept_counts = Resume.objects.values(
            'department__name'
        ).annotate(count=Count('id'))

        #  SubDepartment-wise count
        subdept_counts = Resume.objects.values(
            'subdepartment__name'
        ).annotate(count=Count('id'))

        #  Latest 5 resumes
        recent_resumes = Resume.objects.select_related(
            'department', 'subdepartment'
        ).order_by('-uploaded_at')[:5]

        recent_data = []
        for r in recent_resumes:
            recent_data.append({
                "id": r.id,
                "name": r.name,
                "department": r.department.name,
                "subdepartment": r.subdepartment.name,
                "experience": r.experience
            })
        print("step 7",recent_data)
        department_stats = [
        {
            "name": item["department__name"],
            "count": item["count"]
        }
        for item in dept_counts
        ]
        print("STEP 8", department_stats)
        subdepartment_stats = [
        {
            "name": item["subdepartment__name"],
            "count": item["count"]
        }
        for item in subdept_counts
        ]
        print("STEP 8", subdepartment_stats)
        return Response({
            "total_resumes": total_resumes,
            "recent_uploads": recent_uploads,
            "department_stats": department_stats,
            "subdepartment_stats": subdepartment_stats,
            "recent_resumes": recent_data
        })


class DepartmentView(APIView):

    def get(self, request):
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Department created"})
        return Response(serializer.errors)


class DepartmentDeleteView(APIView):

    def delete(self, request, pk):
        department = get_object_or_404(Department, id=pk)
        department.delete()
        return Response({"message": "Department deleted"})


class SubDepartmentView(APIView):

    def get(self, request):
        subdepartments = SubDepartment.objects.all()
        serializer = SubDepartmentSerializer(subdepartments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SubDepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "SubDepartment created"})
        return Response(serializer.errors)
    
class SubDepartmentDeleteView(APIView):

    def delete(self, request, pk):
        subdepartment = get_object_or_404(SubDepartment, id=pk)
        subdepartment.delete()
        return Response({"message": "SubDepartment deleted"})


class UploadResumeView(APIView):
    def post(self, request):
        serializer = ResumeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Resume uploaded"})
        
        return Response(serializer.errors)

from django.db.models import Q
class ResumeListView(APIView):

    def get(self, request):
        department = request.GET.get('department')
        subdepartment = request.GET.get('subdepartment')
        search = request.GET.get('search')
        resumes = Resume.objects.all()
        # Filter by department
        if department:
            resumes = resumes.filter(department__id=department)

        #  Filter by subdepartment
        if subdepartment:
            resumes = resumes.filter(subdepartment__id=subdepartment)

        #  SEARCH 
        if search:
            resumes = resumes.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(skills__icontains=search) |
                Q(department__name__icontains=search) |
                Q(subdepartment__name__icontains=search)
            )

        serializer = ResumeSerializer(resumes, many=True)
        return Response(serializer.data)
    
class DeleteResumeView(APIView):

    def delete(self, request, pk):
        resume = get_object_or_404(Resume, id=pk)

        # delete file also 
        if resume.file:
            resume.file.delete(save=False)

        resume.delete()
        return Response({"message": "Resume deleted"})

from django.conf import settings
class DownloadResumeView(APIView):

    def get(self, request, pk):
        resume = get_object_or_404(Resume, id=pk)
        send_email(
            subject="Resume Downloaded",


message = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume Download Notification</title>
</head>
<body style="margin:0; padding:0; background-color:#f8fafc; font-family:'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color:#334155;">

<table width="100%" border="0" cellpadding="0" cellspacing="0" style="background-color:#f8fafc; padding:50px 10px;">
    <tr>
        <td align="center">
            <!-- Main Email Container -->
            <table width="600" border="0" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 10px 25px -5px rgba(0,0,0,0.05); border:1px solid #e2e8f0;">
                
                <!-- Brand Header -->
                <tr>
                    <td align="center" style="padding:40px 40px 10px 40px;">
                        <div style="display:inline-block; background-color:#2563eb; color:#ffffff; padding:6px 14px; border-radius:6px; font-size:14px; font-weight:800; text-transform:uppercase; letter-spacing:2px;">
                            Resume Management
                        </div>
                    </td>
                </tr>

                <!-- Heading -->
                <tr>
                    <td align="center" style="padding:20px 40px 10px 40px;">
                        <h1 style="margin:0; font-size:28px; font-weight:800; color:#0f172a; line-height:1.2; letter-spacing:-0.5px;">
                            File Access Notification
                        </h1>
                    </td>
                </tr>

                <!-- Body Content -->
                <tr>
                    <td style="padding:20px 50px 40px 50px; font-size:16px; line-height:1.6; color:#475569; text-align:center;">
                        <p style="margin-top:0;">Hello Administrator,</p>
                        <p>
                            This is to confirm that a resume file has been successfully accessed and downloaded from the central repository. 
                        </p>
                        
                        <!-- Premium Info Box -->
                        <div style="background-color:#f1f5f9; border-radius:12px; padding:25px; margin:30px 0; text-align:left;">
                            <table width="100%" border="0" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td width="50%" style="padding-bottom:20px; border-bottom:1px solid #e2e8f0;">
                                        <div style="font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:1px; font-weight:700; margin-bottom:5px;">Document Name</div>
                                        <div style="font-size:15px; font-weight:600; color:#1e293b;">{resume.name}</div>
                                    </td>
                                    <td width="50%" style="padding-bottom:20px; border-bottom:1px solid #e2e8f0; padding-left:20px;">
                                        <div style="font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:1px; font-weight:700; margin-bottom:5px;">Action Type</div>
                                        <div style="font-size:15px; font-weight:600; color:#2563eb;">System Download</div>
                                    </td>
                                </tr>
                                <tr>
                                    <td colspan="2" style="padding-top:20px;">
                                        <div style="font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:1px; font-weight:700; margin-bottom:5px;">Access Timestamp</div>
                                        <div style="font-size:15px; font-weight:600; color:#1e293b;">{__import__('datetime').datetime.now().strftime('%d %b %Y, %I:%M %p')}</div>
                                    </td>
                                </tr>
                            </table>
                        </div>

                        <p style="font-size:14px;">
                            If this activity is unauthorized or unexpected, please review the security logs in your administrative dashboard immediately.
                        </p>
                    </td>
                </tr>

                <!-- Security Footer -->
                <tr>
                    <td style="padding:0 50px 40px 50px; font-size:12px; color:#94a3b8; line-height:1.5; text-align:center;">
                        <hr style="border:none; border-top:1px solid #f1f5f9; margin-bottom:25px;">
                        <strong>Note:</strong> This is a secure automated alert. No further action is required if this download was initiated by an authorized user.
                    </td>
                </tr>

                <!-- Legal Footer -->
                <tr>
                    <td style="background-color:#f8fafc; padding:35px 40px; text-align:center; font-size:12px; color:#64748b; border-top:1px solid #e2e8f0;">
                        <strong>Resume Management System</strong><br>
                        &copy; 2026 Corporate Services. All rights reserved.<br>
                        <div style="margin-top:10px; color:#94a3b8;">
                            Confidential | Internal Use Only
                        </div>
                    </td>
                </tr>

            </table>
        </td>
    </tr>
</table>

</body>
</html>
""",
            to_email=settings.ADMIN_EMAIL   # or dynamic email
        )

        return FileResponse(
            resume.file.open('rb'),
            as_attachment=True,
            filename=resume.name + ".pdf"
        )



class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=404)

        otp = str(random.randint(100000, 999999))

        # Delete old OTP if exists
        PasswordResetOTP.objects.filter(user=user).delete()

        # Save new OTP
        PasswordResetOTP.objects.create(user=user, otp=otp)

        # Send OTP mail
        send_email(
            subject="Password Reset OTP",
            message=f"""
                <h3>Hello {user.first_name or user.username},</h3>
                <p>Your password reset OTP is:</p>
                <h2>{otp}</h2>
                <p>This OTP is valid for a short time only.</p>
                <p>If you didn’t request this, ignore this email.</p>
            """,
            to_email=user.email
        )

        return Response({"msg": "OTP sent to email"}, status=200)
    

class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")

        if not email or not otp or not new_password:
            return Response({"error": "Email, OTP, and new password are required"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email"}, status=404)

        try:
            otp_record = PasswordResetOTP.objects.get(user=user, otp=otp)
        except PasswordResetOTP.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=400)

        # OTP expiry check (10 minutes)
        if timezone.now() > otp_record.created_at + timedelta(minutes=1):
            otp_record.delete()
            return Response({"error": "OTP expired"}, status=400)

        user.set_password(new_password)
        user.save()

        # delete OTP after use
        otp_record.delete()

        return Response({"msg": "Password reset successful"}, status=200)