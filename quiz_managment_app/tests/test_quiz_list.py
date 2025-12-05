from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from quiz_managment_app.models import Quiz, Question

class QuizListViewTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpassword1")
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword2")

        self.client.force_authenticate(self.user1)

        self.quiz1 = Quiz.objects.create(
            owner=self.user1,
            title="Test Quiz 1",
            description="Das ist ein Test.",
            video_url="https://www.youtube.com/watch?v=abc1"
        )
        self.quiz2 = Quiz.objects.create(
            owner=self.user1,
            title="Test Quiz 2",
            description="Und noch ein Test.",
            video_url="https://www.youtube.com/watch?v=abc2"
        )

        self.quiz3 = Quiz.objects.create(
            owner=self.user2,
            title="Test Quiz 3",
            description="Noch viel mehr Tests.",
            video_url="https://www.youtube.com/watch?v=abc3"
        )

        self.question1 = Question.objects.create(
            quiz=self.quiz1,
            question_title="Question 1",
            question_options=["A", "B", "C", "D"],
            answer="A"
        )

    def test_get_quiz_list_returns_only_user_quizzes(self):
        url = reverse("quiz-list")

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        titles = [quiz["title"] for quiz in response.data]
        self.assertIn("Test Quiz 1", titles)
        self.assertIn("Test Quiz 2", titles)
        self.assertNotIn("Test Quiz 3", titles)

        quiz1_data = next(q for q in response.data if q["id"] == self.quiz1.id)
        self.assertEqual(len(quiz1_data["questions"]), 1)
        self.assertEqual(quiz1_data["questions"][0]["question_title"], "Question 1")
        self.assertEqual(quiz1_data["questions"][0]["question_options"], ["A", "B", "C", "D"])
        self.assertEqual(quiz1_data["questions"][0]["answer"], "A")
        
    def test_quiz_list_unauthenticated(self):
        self.client.force_authenticate(user=None)

        url = reverse("quiz-list")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)