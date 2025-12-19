"""
Unit tests for Task serializers
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task
from tasks.serializers import TaskSerializer


@pytest.mark.django_db
class TestTaskSerializer:
    """Test suite for TaskSerializer"""
    
    def test_serialize_task(self):
        """Test serializing a task"""
        task = Task.objects.create(
            title="Test Task",
            description="Test description",
            status="todo",
            priority=3
        )
        
        serializer = TaskSerializer(task)
        data = serializer.data
        
        assert data['title'] == "Test Task"
        assert data['description'] == "Test description"
        assert data['status'] == "todo"
        assert data['priority'] == 3
        assert 'id' in data
        assert 'created_at' in data
        assert 'updated_at' in data
    
    def test_deserialize_valid_data(self):
        """Test deserializing valid task data"""
        data = {
            'title': 'New Task',
            'description': 'New description',
            'status': 'in_progress',
            'priority': 4
        }
        
        serializer = TaskSerializer(data=data)
        assert serializer.is_valid()
        task = serializer.save()
        
        assert task.title == 'New Task'
        assert task.priority == 4
    
    def test_validate_title_empty(self):
        """Test validation fails for empty title"""
        data = {
            'title': '   ',
            'priority': 3
        }
        
        serializer = TaskSerializer(data=data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors
    
    def test_validate_title_too_short(self):
        """Test validation fails for title less than 3 chars"""
        data = {
            'title': 'AB',
            'priority': 3
        }
        
        serializer = TaskSerializer(data=data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors
    
    def test_validate_priority_out_of_range(self):
        """Test validation fails for invalid priority"""
        data = {
            'title': 'Valid Title',
            'priority': 6
        }
        
        serializer = TaskSerializer(data=data)
        assert not serializer.is_valid()
        assert 'priority' in serializer.errors
    
    def test_validate_status_invalid(self):
        """Test validation fails for invalid status"""
        data = {
            'title': 'Valid Title',
            'status': 'invalid_status'
        }
        
        serializer = TaskSerializer(data=data)
        assert not serializer.is_valid()
        assert 'status' in serializer.errors
    
    def test_is_overdue_field(self):
        """Test is_overdue computed field"""
        past_date = timezone.now() - timedelta(days=1)
        task = Task.objects.create(
            title="Overdue Task",
            due_date=past_date,
            status="todo"
        )
        
        serializer = TaskSerializer(task)
        assert serializer.data['is_overdue'] is True
    
    def test_title_whitespace_trimming(self):
        """Test title whitespace is trimmed"""
        data = {
            'title': '  Task with spaces  ',
            'priority': 3
        }
        
        serializer = TaskSerializer(data=data)
        assert serializer.is_valid()
        task = serializer.save()
        
        assert task.title == 'Task with spaces'


@pytest.mark.django_db
class TestTaskCreateAndUpdate:
    """Test suite for TaskSerializer create and update operations"""
    
    def test_create_with_minimal_data(self):
        """Test creating task with minimal data"""
        data = {'title': 'Minimal Task'}
        
        serializer = TaskSerializer(data=data)
        assert serializer.is_valid()
        task = serializer.save()
        
        assert task.title == 'Minimal Task'
        assert task.status == 'todo'
        assert task.priority == 3

    def test_partial_update(self):
        """Test partial update of task"""
        task = Task.objects.create(
            title="Original",
            status="todo"
        )
        
        data = {'status': 'done'}
        serializer = TaskSerializer(task, data=data, partial=True)
        
        assert serializer.is_valid()
        updated_task = serializer.save()
        
        assert updated_task.status == 'done'
        assert updated_task.title == 'Original'