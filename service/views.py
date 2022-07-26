from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from service.models import Task
from service.serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer
)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        status = self.request.query_params.get("status")

        if status:
            return self.queryset.filter(status__icontains=status)

        return self.queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if self.request.user == instance.author:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)

        if self.request.user == instance.author:
            new_status = self.request.POST["status"]
            if new_status != instance.status:
                pass

            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)

        return Response(status=status.HTTP_403_FORBIDDEN)

    def get_serializer_class(self):
        if self.action == "create":
            return TaskCreateSerializer

        elif self.action in ("update", "partial_update"):
            return TaskUpdateSerializer

        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

