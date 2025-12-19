from rest_framework import serializers
from .models import Task
from django.utils import timezone


class TaskSerializer(serializers.ModelSerializer):
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'due_date', 'created_at', 'updated_at', 'is_overdue'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_overdue']
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()
    
    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters.")
        return value.strip()
    
    def validate_priority(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Priority must be between 1 and 5.")
        return value


class TaskSummarySerializer(serializers.Serializer):
    total_tasks = serializers.IntegerField()
    todo_count = serializers.IntegerField()
    in_progress_count = serializers.IntegerField()
    done_count = serializers.IntegerField()
    overdue_count = serializers.IntegerField()
    high_priority_count = serializers.IntegerField()