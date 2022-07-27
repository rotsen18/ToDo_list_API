from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrSubscriberOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return any(
            [
                request.method in permissions.SAFE_METHODS,
                obj.author == request.user,
                request.user in obj.subscribers.all()
            ]
        )


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class IsSubscriber(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in ("GET", "HEAD", "OPTIONS", "PUT", "PATCH")
            and request.user in obj.subscribers.all()
        )
