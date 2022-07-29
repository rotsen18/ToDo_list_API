import os
import uuid

from django.db import models
from django.db.models.signals import pre_save, m2m_changed, post_save
from django.dispatch import receiver

from todo import settings
from service.tasks import add, send_email


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


temporary_subscribers = None


@receiver(post_save, sender=Task)
def clear_tempory_user_variable(sender, instance, **kwargs):
    global temporary_subscribers
    print("post save", temporary_subscribers)
    temporary_subscribers = None


@receiver(m2m_changed, sender=Task.subscribers.through)
def send_email_if_task_change_subscribers(sender, instance, **kwargs):
    global temporary_subscribers
    new_subscribers = set(instance.subscribers.all())
    old_subscribers = temporary_subscribers
    if old_subscribers is not None and old_subscribers != new_subscribers:
        added_subscribers = new_subscribers.difference(old_subscribers)
        deleted_subscribers = old_subscribers.difference(new_subscribers)
        for subscriber in added_subscribers:
            send_email.delay(
                receiver_name=subscriber.username,
                receiver_email=subscriber.email,
                task=instance.title
            )
        for subscriber in deleted_subscribers:
            send_email.delay(
                receiver_name=subscriber.username,
                receiver_email=subscriber.email,
                task=instance.title,
                subscribed=False
            )
    else:
        temporary_subscribers = new_subscribers


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
