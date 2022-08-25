#from django.contrib.auth.models import User, Group
from rest_framework import serializers
from validator.online.models import File, User, Project, Check, Report, Result, FileTypes

class ProjectSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Project
        fields = [ 'created', 'title', 'type', 'user', 'file' ]

class CheckSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Check
        fields = [ 'created', 'project' ]
        
class ReportSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Report
        fields = [ 'created', 'check1' ]
        
class ResultSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Result
        fields = [ 'created', 'title', 'code', 'report', 'property', 'value', 'success', 'gain' ]
