from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from service.models import Task
from service.serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)
