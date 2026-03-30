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
        fields = ['id', 'name', 'email', 'skills', 'department', 'subdepartment', 'file', 'uploaded_at','experience']

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
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are allowed")
        return value



    
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True) 
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)