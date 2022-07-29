from __future__ import absolute_import, unicode_literals

import time

from celery import shared_task


@shared_task()
def add(x, y):
    print("async=", x + y)
    return


@shared_task()
def send_email(receiver_name: str, receiver_email: str, task: str, subscribed: bool = True):
    action = "subscribed to the task"
    if not subscribed:
        action = "unsubscribed from the task"

    print(f"email to {receiver_name}")
    print(f"adress {receiver_email}")
    print(f"you have been  {action} to task {task}")
    print("-" * 20)
    time.sleep(5)
