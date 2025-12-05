from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from quiz_managment_app.models import Quiz

class QuizDetailViewPatchTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpassword1")
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword2")
        self.client.force_authenticate(self.user1)

        self.quiz = Quiz.objects.create(
            owner=self.user1,
            title="Test Quiz 1",
            description="Das hört gar nicht mehr auf mit den Tests.",
            video_url="https://www.youtube.com/watch?v=abc1"
        )

        self.quiz_other = Quiz.objects.create(
            owner=self.user2,
            title="Test Quiz 2",
            description="Schon wieder einer.",
            video_url="https://www.youtube.com/watch?v=abc2"
        )

    def test_patch_quiz_success(self):
        url = reverse("quiz-detail", args=[self.quiz.pk])
        payload = {"title": "Updated Title", "description": "Updated Desc"}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Updated Title")

    def test_patch_quiz_invalid_data(self):
        url = reverse("quiz-detail", args=[self.quiz.pk])
        payload = {"title": "A"*300}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.data)

    def test_patch_quiz_no_permission(self):
        url = reverse("quiz-detail", args=[self.quiz_other.pk])
        payload = {"title": "Hacked Title"}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, 403)