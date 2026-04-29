from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Resume
from .serializers import *
from django.http import FileResponse, Http404
from django.db import transaction
from .models import Resume, Department, SubDepartment, PasswordResetOTP, User
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Count
from django.utils.timezone import now
import os
import mimetypes
from django.shortcuts import render
import re
from .utils import send_email

from django.utils import timezone
from datetime import timedelta
import random
from rest_framework import status
from django.db.models import Q
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, UserProfileSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import UserResumeSerializer
from .models import UserResume
from .utils import generate_pdf

from .permissions import IsAdminUserCustom

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)
    def put(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Profile updated", "data": serializer.data})
        return Response(serializer.errors, status=400)


class RegisterView(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            #  Send Email (non-blocking)
            email_sent = send_email(
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

            if email_sent:
                return Response({"msg": "User created, confirmation email sent"}, status=201)
            return Response({"msg": "User created, but email failed to deliver"}, status=201)

        return Response(serializer.errors, status=400)


User = get_user_model()
class LoginView(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user_obj = User.objects.filter(email=username).first()
        if user_obj:
            username = user_obj.username

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "username": user.username,
                "email": user.email,
                # On frontend, treat only superuser as admin (full CRUD user/dashboard rights)
                "is_admin": user.is_superuser
            })

        return Response({"error": "Invalid credentials"}, status=401)


class GoogleAuthView(APIView):
    """Token-based Google authentication (for future use or frontend JWT flow)"""
    permission_classes = [AllowAny]

    def post(self, request):
        id_token = request.data.get('id_token') or request.data.get('token')
        if not id_token:
            return Response({'error': 'id_token is required'}, status=400)

        try:
            import requests
            resp = requests.get('https://oauth2.googleapis.com/tokeninfo', params={'id_token': id_token}, timeout=10)
            if resp.status_code != 200:
                return Response({'error': 'Invalid Google token', 'details': resp.text}, status=400)
            google_data = resp.json()

            email = google_data.get('email')
            if not email:
                return Response({'error': 'Google account did not return email'}, status=400)

            user = User.objects.filter(email=email).first()
            created = False
            if not user:
                username_candidate = email.split('@')[0]
                username = username_candidate
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{username_candidate}{counter}"
                    counter += 1

                user = User.objects.create_user(username=username, email=email)
                created = True

            refresh = RefreshToken.for_user(user)
            result = {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_superuser,
                'google_signup': created,
            }

            if created:
                send_email(
                    subject='Welcome from Google Sign-up',
                    message=f"<p>Hi {user.username}, your account was created via Google login.</p>",
                    to_email=user.email
                )

            return Response(result)

        except Exception as e:
            return Response({'error': 'Google auth verification failed', 'details': str(e)}, status=500)

User = get_user_model()


class VerifyOTPView(APIView):
    # permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response({"error": "Email and OTP are required"}, status=400)

        users = User.objects.filter(email=email)

        if not users.exists():
            return Response({"error": "Invalid email"}, status=404)

        user = users.order_by("-id").first()

        otp_record = PasswordResetOTP.objects.filter(user=user).order_by("-created_at").first()

        if not otp_record:
            return Response({"error": "OTP not found"}, status=400)

        # CHECK EXPIRY FIRST
        if timezone.now() > otp_record.created_at + timedelta(minutes=50):
            otp_record.delete()
            return Response({"error": "OTP expired"}, status=400)

        # THEN CHECK CORRECTNESS
        if otp_record.otp != otp:
            return Response({"error": "Invalid OTP"}, status=400)

        return Response({"message": "OTP verified successfully"}, status=200)



class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=400)

        user = User.objects.filter(email=email).order_by("-id").first()

        if not user:
            return Response(
                {"error": "User with this email does not exist"},
                status=404
            )

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))

        print("=== FORGOT PASSWORD DEBUG START ===")
        print("FOR EMAIL:", user.email)
        print("OTP GENERATED:", otp)

        # Save or update OTP
        otp_obj, created = PasswordResetOTP.objects.update_or_create(
            user=user,
            defaults={
                "otp": otp,
                "created_at": timezone.now()
            }
        )

        print("OTP SAVED:", otp_obj.id, otp_obj.otp, otp_obj.user_id)

        # Send OTP email
        email_sent = send_email(
            subject="Password Reset OTP",
            message=f"""
            <div style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>Password Reset Request</h2>
                <p>Hello <strong>{user.first_name or user.username}</strong>,</p>
                <p>Your OTP for password reset is:</p>
                <h1 style="color: #2563eb; letter-spacing: 4px;">{otp}</h1>
                <p>This OTP is valid for <strong>10 minutes</strong>.</p>
                <p>If you did not request this, please ignore this email.</p>
            </div>
            """,
            to_email=user.email
        )
        print("send_mail",email_sent)

        if not email_sent:
            print("EMAIL FAILED, OTP STILL EXISTS IN DB")
            print("=== FORGOT PASSWORD DEBUG END ===")
            return Response(
                {"error": "Failed to send OTP email. Please try again."},
                status=500
            )

        print("EMAIL SENT SUCCESSFULLY")
        print("=== FORGOT PASSWORD DEBUG END ===")

        return Response(
            {"message": "OTP sent successfully"},
            status=200
        )


class ResetPasswordView(APIView):
    # permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")

        if not email or not otp or not new_password:
            return Response(
                {"error": "Email, OTP, and new password are required"},
                status=400
            )

        users = User.objects.filter(email=email)

        if not users.exists():
            return Response({"error": "Invalid email"}, status=404)

        user = users.order_by("-id").first()

        otp_record = PasswordResetOTP.objects.filter(user=user).order_by("-created_at").first()

        if not otp_record:
            return Response({"error": "OTP not found"}, status=400)

        # CHECK EXPIRY FIRST
        if timezone.now() > otp_record.created_at + timedelta(minutes=1):
            otp_record.delete()
            return Response({"error": "OTP expired"}, status=400)

        # THEN CHECK CORRECTNESS
        if otp_record.otp != otp:
            return Response({"error": "Invalid OTP"}, status=400)

        # Password validations
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
    permission_classes = [IsAdminUserCustom]

    def get(self, request):

        total_resumes = Resume.objects.count()

        # Recent uploads (last 7 days)
        last_7_days = now() - timedelta(days=7)
        recent_uploads = Resume.objects.filter(
            uploaded_at__gte=last_7_days
        ).count()

        # SAP & WEB counts
        sap_count = Resume.objects.filter(
            department__name__iexact="sap"
        ).count()

        web_count = Resume.objects.filter(
            department__name__iexact="web"
        ).count()

        # Latest 5 resumes
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

        return Response({
            "total_resumes": total_resumes,
            "recent_uploads": recent_uploads,
            "sap_count": sap_count,
            "web_count": web_count,
            "recent_resumes": recent_data
        })

class DepartmentView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUserCustom()]

    def get(self, request):
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class DepartmentDeleteView(APIView):
    permission_classes = [IsAdminUserCustom]
    def delete(self, request, pk):
        department = get_object_or_404(Department, id=pk)
        department.delete()
        return Response({"message": "Department deleted"})

class SubDepartmentView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUserCustom()]

    def get(self, request):
        subdepartments = SubDepartment.objects.all()
        serializer = SubDepartmentSerializer(subdepartments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SubDepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
class SubDepartmentDeleteView(APIView):
    permission_classes = [IsAdminUserCustom]

    def delete(self, request, pk):
        subdepartment = get_object_or_404(SubDepartment, id=pk)
        subdepartment.delete()
        return Response({"message": "SubDepartment deleted"})
from rest_framework.parsers import MultiPartParser, FormParser

class UploadResumeView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        print("UPLOAD USER:", request.user.id, request.user.username)
        print("FILES:", request.FILES)
        print("DATA:", request.data)

        file = request.FILES.get("file")

        if not file:
            return Response({"error": "No file provided"}, status=400)

        data = request.data.copy()
        data["file"] = file   #  VERY IMPORTANT

        serializer = ResumeSerializer(data=data)

        if serializer.is_valid():
            resume = serializer.save(user=request.user)
            resume.file.resource_type = "auto"

            return Response({
                "message": "Uploaded",
                "file_url": resume.file.url   #  Cloudinary URL
            }, status=201)

        print("ERRORS:", serializer.errors)
        return Response(serializer.errors, status=400)    
    
class ResumeListView(APIView):
    permission_classes = [IsAdminUserCustom]

    def get(self, request):
        department = request.GET.get('department')
        subdepartment = request.GET.get('subdepartment')
        search = request.GET.get('search')

        print("Dept:", department, "Sub:", subdepartment)

        resumes = Resume.objects.select_related(
            'department', 'subdepartment'
        ).all()

        #  Department filter
        if department:
            resumes = resumes.filter(department_id=department)

        # Subdepartment filter (ONLY if valid)
        if subdepartment and subdepartment != "":
            resumes = resumes.filter(subdepartment_id=subdepartment)

        # 🔍 Search
        if search:
            resumes = resumes.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(skills__icontains=search)
            )
        resumes = resumes.order_by('-is_bookmarked', '-uploaded_at')

        serializer = ResumeSerializer(resumes, many=True)
        return Response(serializer.data)
   
import cloudinary.uploader
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class DeleteResumeView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        resume = get_object_or_404(Resume, id=pk)

        try:
            # DELETE FROM CLOUDINARY
            if resume.file:
                public_id = resume.file.public_id   # VERY IMPORTANT
                cloudinary.uploader.destroy(public_id, resource_type="raw")

            #  DELETE FROM DATABASE
            resume.delete()

            return Response({"message": "Deleted successfully"}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from django.utils.timezone import now
from django.conf import settings

from .models import Resume
from .utils import send_email
import requests


class DownloadResumeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        # 🔍 Get resume
        resume = get_object_or_404(Resume, id=pk)

        # ❌ If no file
        if not resume.file:
            return HttpResponse("File not found", status=404)

        try:
            # 🌐 Get Cloudinary URL
            file_url = resume.file.url

            # 🔥 Fetch file from Cloudinary
            response = requests.get(file_url)

            if response.status_code != 200:
                return HttpResponse("Failed to fetch file", status=500)

            # 📧 SEND EMAIL (ADDED - without breaking your flow)
            try:
                user_name = (
                    request.user.username
                    if request.user.is_authenticated
                    else "Anonymous"
                )

                message = f"""
<!DOCTYPE html>
<html>
<body>
<p>Resume <strong>{resume.name}</strong> was downloaded</p>
<p><strong>Email:</strong> {resume.email}</p>
<p><strong>Downloaded by:</strong> {user_name}</p>
<p><strong>Time:</strong> {now()}</p>
</body>
</html>
"""

                send_email(
                    subject="Resume Downloaded",
                    message=message,
                    to_email=settings.ADMIN_EMAIL
                )

            except Exception as email_error:
                print("Email error:", email_error)

            # 🔥 FORCE DOWNLOAD (your original logic)
            file_response = HttpResponse(
                response.content,
                content_type="application/pdf"
            )
            file_response["Content-Disposition"] = f'attachment; filename="{resume.name}.pdf"'

            return file_response

        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)        

# from django.shortcuts import get_object_or_404, redirect
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import AllowAny
# from django.utils.timezone import now
# from django.conf import settings

# from .models import Resume
# from .utils import send_email
# import requests
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404
# from rest_framework.views import APIView
# from rest_framework.permissions import AllowAny

# from .models import Resume


# class DownloadResumeView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request, pk):
#         resume = get_object_or_404(Resume, id=pk)

#         if not resume.file:
#             return HttpResponse("File not found", status=404)

#         try:
#             file_url = resume.file.url

#             response = requests.get(file_url)

#             if response.status_code != 200:
#                 return HttpResponse("Failed to fetch file", status=500)

#             #  THIS LINE FORCES DOWNLOAD
#             file_response = HttpResponse(
#                 response.content,
#                 content_type="application/pdf"
#             )
#             file_response["Content-Disposition"] = f'attachment; filename="{resume.name}.pdf"'

#             return file_response

#         except Exception as e:
#             return HttpResponse(f"Error: {str(e)}", status=500)


# class DownloadResumeView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request, pk):
#         # 🔍 Get resume
#         resume = get_object_or_404(Resume, id=pk)

#         # ❌ If no file
#         if not resume.file:
#             return Response({"error": "File not found"}, status=404)

#         try:
#             # 🌐 Cloudinary URL
#             file_url = resume.file.url

#             # 🔥 FIX CLOUDINARY TYPE (IMPORTANT)
#             # Converts image → raw (needed for PDFs/docs)
            

#             # 🔥 FORCE DOWNLOAD
#             download_url = file_url.replace(
#                 "/upload/", "/upload/fl_attachment/"
#             )

#             # 📧 SEND EMAIL (optional)
#             try:
#                 message = f"""
# <h3>Resume Downloaded</h3>
# <p><strong>Name:</strong> {resume.name}</p>
# <p><strong>Email:</strong> {resume.email}</p>
# <p><strong>Downloaded by:</strong> {request.user.username if request.user.is_authenticated else 'Anonymous'}</p>
# <p><strong>Time:</strong> {now()}</p>
# """
#                 send_email(
#                     subject="Resume Downloaded",
#                     message=message,
#                     to_email=settings.DEFAULT_FROM_EMAIL
#                 )
#             except Exception as e:
#                 print("Email error:", e)

#             # 🚀 Redirect to download
#             return redirect(download_url)

#         except Exception as e:
#             return Response(
#                 {"error": f"Download failed: {str(e)}"},
#                 status=500
#             )

class CreateResume(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserResumeSerializer(data=request.data)

        if serializer.is_valid():
            resume = serializer.save(user=request.user)

            file_path = generate_pdf(resume)
            resume.file = file_path
            resume.save()

            return Response({
                "message": "Resume created",
                "file_url": resume.file.url
            })

        return Response(serializer.errors, status=400)


class MyResumes(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        resumes = UserResume.objects.filter(user=request.user)

        return Response([
            {
                "id": r.id,
                "title": r.title,
                "file": r.file.url if r.file else None
            }
            for r in resumes
        ])
        
        
class MyUploadHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        resumes = Resume.objects.filter(user=request.user).select_related(
            'department', 'subdepartment'
        ).order_by('-uploaded_at')

        data = []
        for r in resumes:
            data.append({
                "id": r.id,
                "name": r.name,
                "email": r.email,
                "skills": r.skills,
                "experience": r.experience,
                "department": r.department.name,
                "subdepartment": r.subdepartment.name,
                "file": r.file.url if r.file else None,
                "uploaded_at": r.uploaded_at,
            })

        return Response(data)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class ResumeHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # 🔐 Check user
            user = request.user
            print("CURRENT USER:", user)

            # 📊 Get data
            if user.is_superuser:
                resumes = Resume.objects.all().select_related('user', 'department', 'subdepartment')
            else:
                resumes = Resume.objects.filter(user=user).select_related('user', 'department', 'subdepartment')

            data = []

            for r in resumes:
                try:
                    data.append({
                        "id": r.id,
                        "filename": (r.file.name.split("/")[-1] if r.file else r.name),
                        "uploaded_at": r.uploaded_at,
                        "user": (r.user.username if r.user else "Unknown"),
                        "department": getattr(r.department, "name", "N/A"),
                        "subdepartment": getattr(r.subdepartment, "name", None),
                    })
                except Exception as e:
                    print(f"❌ Error in resume {r.id}: {e}")  # debug per row

            return Response(data)

        except Exception as e:
            print("❌ GLOBAL ERROR:", str(e))
            return Response({"error": str(e)}, status=500)    
    
    
# class ResumeHistoryView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         if request.user.is_superuser:
#             resumes = Resume.objects.all()
#         else:
#             resumes = Resume.objects.filter(user=request.user)

#         data = []
#         for r in resumes:
#             data.append({
#                 "id": r.id,
#                 "filename": r.file.name.split("/")[-1] if r.file else r.name,
#                 "uploaded_at": r.uploaded_at,
#                 "user": r.user.username if r.user else "Unknown",
#                 "department": r.department.name,
#                 "subdepartment": r.subdepartment.name if r.subdepartment else None,
#             })

#         return Response(data)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Resume


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_bookmark(request, pk):
    try:
        resume = Resume.objects.get(pk=pk)

        resume.is_bookmarked = not resume.is_bookmarked
        resume.save()

        return Response({
            "id": resume.id,
            "is_bookmarked": resume.is_bookmarked
        })

    except Resume.DoesNotExist:
        return Response({"error": "Resume not found"}, status=404)