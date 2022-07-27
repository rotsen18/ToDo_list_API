from rest_framework import serializers

from service.models import Task


class TaskSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="username"
    )
    subscribers = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="username"
    )

    class Meta:
        model = Task
        fields = "__all__"


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("title", "description", "subscribers")
        read_only_fields = ("id", "author", "status")


class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("title", "status", "description", "subscribers")
        read_only_fields = ("id", "author")


class TaskChangeStatusNotOwnerSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=(("Active", "Active"), ))

    class Meta:
        model = Task
        fields = ("status", )
