"""
Unit tests for Task API endpoints (Views)
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from tasks.models import Task


@pytest.fixture
def api_client():
    """Fixture to create API client for testing"""
    return APIClient()


@pytest.fixture
def sample_task():
    """Fixture to create a sample task for testing"""
    return Task.objects.create(
        title="Sample Task",
        description="Sample description",
        status="todo",
        priority=3
    )


@pytest.mark.django_db
class TestTaskListEndpoint:
    """Test GET /api/tasks/ - List all tasks"""
    
    def test_list_tasks_empty(self, api_client):
        """Test listing tasks when database is empty"""
        response = api_client.get('/api/tasks/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert response.data['results'] == []
    
    def test_list_tasks_with_data(self, api_client):
        """Test listing tasks returns all tasks"""
        # Create multiple tasks
        Task.objects.create(title="Task 1", priority=1)
        Task.objects.create(title="Task 2", priority=2)
        Task.objects.create(title="Task 3", priority=3)
        
        response = api_client.get('/api/tasks/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        assert len(response.data['results']) == 3


@pytest.mark.django_db
class TestTaskCreateEndpoint:
    """Test POST /api/tasks/ - Create new task"""
    
    def test_create_task_with_valid_data(self, api_client):
        """Test creating a task with valid data"""
        data = {
            'title': 'New Task',
            'description': 'New description',
            'status': 'todo',
            'priority': 4
        }
        
        response = api_client.post('/api/tasks/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Task'
        assert response.data['priority'] == 4
        assert 'id' in response.data
        
        # Verify task was created in database
        assert Task.objects.count() == 1
        task = Task.objects.first()
        assert task.title == 'New Task'
    
    def test_create_task_with_minimal_data(self, api_client):
        """Test creating task with only required fields"""
        data = {'title': 'Minimal Task'}
        
        response = api_client.post('/api/tasks/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Minimal Task'
        assert response.data['status'] == 'todo'  # Default value
        assert response.data['priority'] == 3  # Default value
    
    def test_create_task_with_invalid_data(self, api_client):
        """Test creating task with invalid data fails"""
        data = {
            'title': 'AB',  # Too short (min 3 chars)
            'priority': 10  # Out of range (max 5)
        }
        
        response = api_client.post('/api/tasks/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data
        assert 'priority' in response.data
    
    def test_create_task_without_title(self, api_client):
        """Test creating task without title fails"""
        data = {'priority': 3}
        
        response = api_client.post('/api/tasks/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data


@pytest.mark.django_db
class TestTaskDetailEndpoint:
    """Test GET /api/tasks/{id}/ - Get single task"""
    
    def test_get_existing_task(self, api_client, sample_task):
        """Test retrieving an existing task"""
        response = api_client.get(f'/api/tasks/{sample_task.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(sample_task.id)
        assert response.data['title'] == 'Sample Task'
    
    def test_get_nonexistent_task(self, api_client):
        """Test retrieving a non-existent task returns 404"""
        fake_id = '00000000-0000-0000-0000-000000000000'
        response = api_client.get(f'/api/tasks/{fake_id}/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTaskUpdateEndpoint:
    """Test PUT/PATCH /api/tasks/{id}/ - Update task"""
    
    def test_partial_update_task(self, api_client, sample_task):
        """Test updating a task with PATCH (partial update)"""
        data = {'status': 'done'}
        
        response = api_client.patch(
            f'/api/tasks/{sample_task.id}/',
            data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'done'
        assert response.data['title'] == 'Sample Task'  # Unchanged
        
        # Verify in database
        sample_task.refresh_from_db()
        assert sample_task.status == 'done'
    
    def test_full_update_task(self, api_client, sample_task):
        """Test updating a task with PUT (full update)"""
        data = {
            'title': 'Updated Task',
            'description': 'Updated description',
            'status': 'in_progress',
            'priority': 5
        }
        
        response = api_client.put(
            f'/api/tasks/{sample_task.id}/',
            data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Task'
        assert response.data['status'] == 'in_progress'
        assert response.data['priority'] == 5


@pytest.mark.django_db
class TestTaskDeleteEndpoint:
    """Test DELETE /api/tasks/{id}/ - Delete task"""
    
    def test_delete_existing_task(self, api_client, sample_task):
        """Test deleting an existing task"""
        task_id = sample_task.id
        
        response = api_client.delete(f'/api/tasks/{task_id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        
        # Verify task was deleted from database
        assert Task.objects.filter(id=task_id).count() == 0
    
    def test_delete_nonexistent_task(self, api_client):
        """Test deleting a non-existent task returns 404"""
        fake_id = '00000000-0000-0000-0000-000000000000'
        response = api_client.delete(f'/api/tasks/{fake_id}/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTaskFiltering:
    """Test filtering functionality on /api/tasks/"""
    
    def setup_method(self):
        """Create sample tasks with different statuses and priorities"""
        Task.objects.create(title="High Priority Task", priority=5, status="todo")
        Task.objects.create(title="Low Priority Task", priority=1, status="todo")
        Task.objects.create(title="Done Task", priority=3, status="done")
        Task.objects.create(title="In Progress Task", priority=4, status="in_progress")
    
    def test_filter_by_status(self, api_client):
        """Test filtering tasks by status"""
        response = api_client.get('/api/tasks/?status=todo')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        for task in response.data['results']:
            assert task['status'] == 'todo'
    
    def test_filter_by_priority(self, api_client):
        """Test filtering tasks by priority"""
        response = api_client.get('/api/tasks/?priority=5')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['priority'] == 5
    
    def test_filter_by_status_and_priority(self, api_client):
        """Test filtering by multiple parameters"""
        response = api_client.get('/api/tasks/?status=todo&priority=5')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        result = response.data['results'][0]
        assert result['status'] == 'todo'
        assert result['priority'] == 5
    
    def test_search_in_title(self, api_client):
        """Test searching tasks by title"""
        response = api_client.get('/api/tasks/?search=High')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1
        assert 'High' in response.data['results'][0]['title']


@pytest.mark.django_db
class TestTaskPagination:
    """Test pagination functionality"""
    
    def test_pagination_first_page(self, api_client):
        """Test getting first page of results"""
        # Create 10 tasks (page size is 8)
        for i in range(10):
            Task.objects.create(title=f"Task {i}", priority=3)
        
        response = api_client.get('/api/tasks/?page=1')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 10
        assert len(response.data['results']) == 8  # Page size
        assert response.data['next'] is not None
        assert response.data['previous'] is None
    
    def test_pagination_second_page(self, api_client):
        """Test getting second page of results"""
        # Create 10 tasks
        for i in range(10):
            Task.objects.create(title=f"Task {i}", priority=3)
        
        response = api_client.get('/api/tasks/?page=2')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2  # Remaining tasks
        assert response.data['previous'] is not None
        assert response.data['next'] is None
    
    def test_pagination_invalid_page(self, api_client):
        """Test requesting page that doesn't exist"""
        Task.objects.create(title="Task 1", priority=3)
        
        response = api_client.get('/api/tasks/?page=999')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCustomActions:
    """Test custom actions: mark_done, mark_in_progress, summary"""
    
    def test_mark_task_done(self, api_client, sample_task):
        """Test marking a task as done"""
        response = api_client.post(f'/api/tasks/{sample_task.id}/mark_done/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'done'
        
        # Verify in database
        sample_task.refresh_from_db()
        assert sample_task.status == 'done'
    
    def test_mark_task_in_progress(self, api_client, sample_task):
        """Test marking a task as in progress"""
        response = api_client.post(f'/api/tasks/{sample_task.id}/mark_in_progress/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'in_progress'
        
        # Verify in database
        sample_task.refresh_from_db()
        assert sample_task.status == 'in_progress'
    
    def test_summary_endpoint(self, api_client):
        """Test getting task summary statistics"""
        # Create tasks with different statuses
        Task.objects.create(title="Todo Task", status="todo", priority=5)
        Task.objects.create(title="Done Task", status="done", priority=3)
        Task.objects.create(title="In Progress Task", status="in_progress", priority=4)
        
        response = api_client.get('/api/tasks/summary/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_tasks'] == 3
        assert response.data['todo_count'] == 1
        assert response.data['done_count'] == 1
        assert response.data['in_progress_count'] == 1
        assert response.data['high_priority_count'] == 2  # Priority >= 4


@pytest.mark.django_db
class TestComputedFields:
    """Test computed fields in API responses"""
    
    def test_is_overdue_field_true(self, api_client):
        """Test is_overdue is true for overdue tasks"""
        past_date = timezone.now() - timedelta(days=1)
        task = Task.objects.create(
            title="Overdue Task",
            due_date=past_date,
            status="todo"
        )
        
        response = api_client.get(f'/api/tasks/{task.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_overdue'] is True
    
    def test_is_overdue_field_false(self, api_client):
        """Test is_overdue is false for future tasks"""
        future_date = timezone.now() + timedelta(days=1)
        task = Task.objects.create(
            title="Future Task",
            due_date=future_date,
            status="todo"
        )
        
        response = api_client.get(f'/api/tasks/{task.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_overdue'] is False
    
    def test_is_overdue_field_no_due_date(self, api_client):
        """Test is_overdue is false when no due_date"""
        task = Task.objects.create(title="No Deadline Task", status="todo")
        
        response = api_client.get(f'/api/tasks/{task.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_overdue'] is False
