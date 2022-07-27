from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from service.models import Task
from service.permissions import IsOwnerOrReadOnly, IsSubscriber
from service.serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    TaskChangeStatusNotOwnerSerializer
)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly | IsSubscriber)

    def get_serializer_class(self):
        if self.action == "create":
            return TaskCreateSerializer

        elif self.action in ("update", "partial_update"):
            task = self.get_object()

            if self.request.user == task.author:
                return TaskUpdateSerializer

            if self.request.user in task.subscribers.all():
                if self.request.POST.get("status") != task.status:
                    return TaskChangeStatusNotOwnerSerializer

        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
