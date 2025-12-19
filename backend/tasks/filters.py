from django_filters import rest_framework as filters
from .models import Task
from django.utils import timezone


class TaskFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=Task.STATUS_CHOICES)
    priority = filters.NumberFilter()
    priority_min = filters.NumberFilter(field_name='priority', lookup_expr='gte')
    priority_max = filters.NumberFilter(field_name='priority', lookup_expr='lte')
    title_contains = filters.CharFilter(field_name='title', lookup_expr='icontains')
    
    class Meta:
        model = Task
        fields = ['status', 'priority']