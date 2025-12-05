from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from quiz_managment_app.models import Quiz, Question

class QuizDetailViewGetTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpassword1")
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword2")
        self.client.force_authenticate(self.user1)

        self.quiz = Quiz.objects.create(
            owner=self.user1,
            title="Test Quiz 1",
            description="Da ist wieder ein Test.",
            video_url="https://www.youtube.com/watch?v=abc1"
        )

        self.question = Question.objects.create(
            quiz=self.quiz,
            question_title="Question 1",
            question_options=["A", "B", "C", "D"],
            answer="A"
        )

        self.quiz_other = Quiz.objects.create(
            owner=self.user2,
            title="Test Quiz 2",
            description="Und schon wieder einer.",
            video_url="https://www.youtube.com/watch?v=abc2"
        )

    def test_get_quiz_success(self):
        url = reverse("quiz-detail", args=[self.quiz.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Test Quiz 1")
        self.assertEqual(len(response.data["questions"]), 1)

    def test_get_quiz_no_permission(self):
        url = reverse("quiz-detail", args=[self.quiz_other.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)