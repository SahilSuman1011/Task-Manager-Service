from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.utils import timezone

from .models import Task
from .serializers import TaskSerializer, TaskSummarySerializer
from .filters import TaskFilter


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = TaskFilter
    ordering_fields = ['created_at', 'updated_at', 'due_date', 'priority']
    ordering = ['-created_at']
    search_fields = ['title', 'description']
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        task_id = instance.id
        self.perform_destroy(instance)
        return Response(
            {'message': f'Task {task_id} deleted successfully'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        now = timezone.now()
        total_tasks = Task.objects.count()
        todo_count = Task.objects.filter(status='todo').count()
        in_progress_count = Task.objects.filter(status='in_progress').count()
        done_count = Task.objects.filter(status='done').count()
        overdue_count = Task.objects.filter(due_date__lt=now).exclude(status='done').count()
        high_priority_count = Task.objects.filter(priority__gte=4).count()
        
        data = {
            'total_tasks': total_tasks,
            'todo_count': todo_count,
            'in_progress_count': in_progress_count,
            'done_count': done_count,
            'overdue_count': overdue_count,
            'high_priority_count': high_priority_count,
        }
        
        serializer = TaskSummarySerializer(data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_done(self, request, pk=None):
        task = self.get_object()
        task.status = 'done'
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_in_progress(self, request, pk=None):
        task = self.get_object()
        task.status = 'in_progress'
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)