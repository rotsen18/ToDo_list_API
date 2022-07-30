from __future__ import absolute_import, unicode_literals

from celery import shared_task
from django.core.mail import send_mail

from todo import settings


@shared_task()
def send_email(receiver_email: str, task: str, subscribed: bool = True):
    if receiver_email:
        action = "subscribed to the task:"
        if not subscribed:
            action = "unsubscribed from the task:"

        message = f"You have been {action} {task}"

        send_mail(
            subject="ToDo list task new action",
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[receiver_email],
            fail_silently=False,
        )
