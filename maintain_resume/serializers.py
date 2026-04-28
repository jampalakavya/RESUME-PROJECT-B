from rest_framework import serializers
from .models import Department, SubDepartment, Resume
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

class SubDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubDepartment
        fields = ['id', 'name', 'department']

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['id', 'name', 'email', 'skills', 'department', 'subdepartment', 'file', 'uploaded_at','experience','is_bookmarked']

    def validate(self, data):
        department = data.get('department')
        subdepartment = data.get('subdepartment')
        #  Required check 
        if not department or not subdepartment:
            raise serializers.ValidationError(
                "Department and SubDepartment are required"
            )
        #  Relationship check
        if subdepartment.department != department:
            raise serializers.ValidationError(
                "SubDepartment does not belong to selected Department"
            )
        return data
    def validate_file(self, value):
        allowed_ext = ('.pdf', '.doc', '.docx')
        if not value.name.lower().endswith(allowed_ext):
            raise serializers.ValidationError("Only PDF, DOC, and DOCX files are allowed")
        return value

# serializers.py
from rest_framework import serializers
from .models import (
    UserResume, Education, Experience, Project,
    Skill, Certification, Achievement, Language
)

# -------- CHILD --------

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['degree', 'institution', 'year']


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['job_title', 'company', 'description']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['title', 'description']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['name']


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['name']


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['title']


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['name']


# -------- MAIN --------

class UserResumeSerializer(serializers.ModelSerializer):
    educations = EducationSerializer(many=True)
    experiences = ExperienceSerializer(many=True)
    projects = ProjectSerializer(many=True)
    skills = SkillSerializer(many=True)
    certifications = CertificationSerializer(many=True)
    achievements = AchievementSerializer(many=True)
    languages = LanguageSerializer(many=True)

    class Meta:
        model = UserResume
        fields = '__all__'
        read_only_fields = ['user', 'file']

    def create(self, validated_data):
        educations = validated_data.pop('educations', [])
        experiences = validated_data.pop('experiences', [])
        projects = validated_data.pop('projects', [])
        skills = validated_data.pop('skills', [])
        certifications = validated_data.pop('certifications', [])
        achievements = validated_data.pop('achievements', [])
        languages = validated_data.pop('languages', [])

        resume = UserResume.objects.create(**validated_data)

        for item in educations:
            Education.objects.create(resume=resume, **item)

        for item in experiences:
            Experience.objects.create(resume=resume, **item)

        for item in projects:
            Project.objects.create(resume=resume, **item)

        for item in skills:
            Skill.objects.create(resume=resume, **item)

        for item in certifications:
            Certification.objects.create(resume=resume, **item)

        for item in achievements:
            Achievement.objects.create(resume=resume, **item)

        for item in languages:
            Language.objects.create(resume=resume, **item)

        return resume
    
    
    
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


# ---------------- AUTH SERIALIZERS ----------------

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']