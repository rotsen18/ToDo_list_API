import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from service.tests.test_task_api import (
    TASK_URL,
    sample_task,
    sample_user,
    detail_url
)


def image_upload_url(task_id):
    """Return URL for recipe image upload"""
    return reverse("service:task-upload-image", args=[task_id])


class TaskImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "testUser",
            "test12345"
        )
        self.client.force_authenticate(self.user)
        self.task = sample_task(author=self.user)

    def tearDown(self):
        self.task.images.all().delete()

    def test_upload_image_to_task(self):
        """Test uploading an image to task"""
        url = image_upload_url(self.task.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.task.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.task.images.first().image.path))

    def test_upload_image_to_task_not_owner_forbidden(self):
        """Test uploading an image to task without permissions"""
        author = sample_user()
        task = sample_task(author=author)
        url = image_upload_url(task.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        task.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.task.id)
        response = self.client.post(
            url, {"image": "not image"},
            format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_image_url_is_shown_on_task_detail(self):
        url = image_upload_url(self.task.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        response = self.client.get(detail_url(self.task.id))

        self.assertIn("image", response.data["images"][0])

    def test_image_url_is_shown_on_task_list(self):
        url = image_upload_url(self.task.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        response = self.client.get(TASK_URL)

        self.assertIn("image", response.data[0]["images"][0])
