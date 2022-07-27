from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from service.models import Task
from service.permissions import IsOwnerOrReadOnly, IsSubscriber
from service.serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    TaskChangeStatusNotOwnerSerializer, TaskImageSerializer
)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly | IsSubscriber)

    def get_queryset(self):
        queryset = Task.objects.select_related("author")
        status = self.request.query_params.get("status")

        if status:
            return queryset.filter(status__icontains=status)

        return queryset

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

        elif self.action == "upload_image":
            return TaskImageSerializer

        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAuthenticated],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific task"""
        task = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if request.user == task.author:
                serializer.save(task=task)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
