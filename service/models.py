import os
import uuid

from django.db import models

from todo import settings


class Task(models.Model):
    STATUSES = [
        ("New", "New"),
        ("Active", "Active"),
        ("Closed", "Closed")
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=31, choices=STATUSES, default="New")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    subscribers = models.ManyToManyField(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


def task_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{uuid.uuid4()}{extension}"

    return os.path.join("uploads/task_images/", filename)


class Image(models.Model):
    task = models.ForeignKey(
        "Task",
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to=task_image_file_path)

    def __str__(self):
        return f"image_{self.id}_{self.task}"
