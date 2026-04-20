
from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('signup/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('google-auth/', GoogleAuthView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('my-upload-history/', MyUploadHistoryView.as_view()),
    path("resumes/history/", ResumeHistoryView.as_view()),
    
    path("resumes/<int:pk>/bookmark/", toggle_bookmark),

    #  Department
    path('departments/', DepartmentView.as_view()),     # GET (list), POST (create)
    path('departments/delete/<int:pk>/', DepartmentDeleteView.as_view()),

    #  SubDepartment
    path('subdepartments/', SubDepartmentView.as_view()), # GET (list), POST (create)
    path('subdepartments/delete/<int:pk>/', SubDepartmentDeleteView.as_view()),

    #  Resume
    path('resumes/upload/', UploadResumeView.as_view()), # POST
    path('resumes/', ResumeListView.as_view()),          # GET
    path('resumes/delete/<int:pk>/', DeleteResumeView.as_view()),
    path('resumes/download/<int:pk>/', DownloadResumeView.as_view()),
    
    
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    # urls.py
    path("user-resume/create/", CreateResume.as_view()),
    path("user-resume/list/", MyResumes.as_view()),
]