from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from service.models import Task
from service.serializers import TaskSerializer


TASK_URL = reverse("service:task-list")


def sample_user(**params):
    defaults = {
        "username": "bob33",
        "password": "test12345",
    }
    defaults.update(params)

    return get_user_model().objects.create_user(**defaults)


def sample_task(**params):
    defaults = {
        "title": "Sample title of task",
        "description": "Sample description",
        "status": "New",
    }
    defaults.update(params)

    return Task.objects.create(**defaults)


def detail_url(task_id: int):
    return reverse("service:task-detail", args=[task_id])


class UnauthenticatedTaskApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TASK_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTaskApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "testUser",
            "test12345"
        )
        self.client.force_authenticate(self.user)

    def test_filter_task_by_status(self):
        author = sample_user()
        sample_task(title="title 1", author=author)
        sample_task(title="title 2", author=author)
        sample_task(title="title 3", author=author, status="Active")
        filter_status = "New"

        response = self.client.get(TASK_URL, {"status": filter_status})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for task in response.data:
            self.assertEqual(task["status"], filter_status)

    def test_retrieve_task_detail(self):
        author = sample_user()
        task = sample_task(title="title 1", author=author)
        url = detail_url(task.id)

        response = self.client.get(url)

        serializer = TaskSerializer(task)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_edit_task_not_owner_forbidden(self):
        author = sample_user()
        task = sample_task(title="title 1", author=author)
        url = detail_url(task.id)
        payload = {"title": "new title"}

        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_task_not_owner_forbidden(self):
        author = sample_user()
        task = sample_task(title="title 1", author=author)
        url = detail_url(task.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_change_task_status_subscriber(self):
        author = sample_user()
        subscriber = sample_user(username="test_subscriber")
        task = sample_task(title="title 1", author=author)
        url = detail_url(task.id)
        payload = {"status": "Active"}

        task.subscribers.add(subscriber)
        task.save()
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        task.subscribers.add(self.user)
        task.save()
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payload = {"status": "Closed"}
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_task_status_owner(self):
        task_1 = sample_task(title="title 1", author=self.user)
        task_2 = sample_task(
            title="title 2",
            author=self.user,
            status="Active"
        )
        payload = {"status": "Closed"}

        for task in (task_1, task_2):
            url = detail_url(task.id)

            response = self.client.patch(url, payload)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
