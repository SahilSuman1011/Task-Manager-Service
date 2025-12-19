import pytest
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task


@pytest.mark.django_db
class TestTaskModel:
    def test_create_task(self):
        task = Task.objects.create(title="Test Task", priority=3)
        assert task.title == "Test Task"
        assert task.status == "todo"
        assert task.priority == 3
    
    def test_task_is_overdue(self):
        past_date = timezone.now() - timedelta(days=1)
        task = Task.objects.create(title="Test", due_date=past_date, status="todo")
        assert task.is_overdue() is True