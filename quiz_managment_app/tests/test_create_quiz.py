import os
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from unittest.mock import patch


class CreateQuizTest(APITestCase):
    """
    Test case for the QuizCreateView API, verifying quiz creation
    from a YouTube URL.
    """
    def setUp(self):
        """
        Sets up the test user, authentication, and example payloads.
        """
        os.environ["GOOGLE_API_KEY"] = "dummy-test-key"
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword"
        )
        self.client.force_authenticate(self.user)

        self.valid_payload = {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        self.invalid_payload = {
            "url": "https://www.invalid.com/watch?v=123"
        }

    @patch("quiz_managment_app.api.views.QuizGenerator.fetch_audio_from_url")
    @patch("quiz_managment_app.api.views.QuizGenerator.transcribe_audio")
    @patch("quiz_managment_app.api.views.QuizGenerator.generate_quiz")
    @patch("quiz_managment_app.api.views.QuizGenerator.clean_quiz_text")

    def test_create_quiz_success(
        self,
        mock_clean_text,
        mock_generate_quiz,
        mock_transcribe,
        mock_fetch_audio,
    ):
        """
        Tests successful quiz creation by mocking audio processing,
        transcription, and AI quiz generation.
        """
        mock_fetch_audio.return_value = None
        mock_transcribe.return_value = "Mock transcript"
        mock_generate_quiz.return_value = "{" \
            '"title": "Test Quiz",' \
            '"description": "Mock description",' \
            '"questions": [{"question_title": "What is 2+2?", "question_options": ["1","2","3","4"], "answer": "4"}]' \
            "}"
        mock_clean_text.return_value = mock_generate_quiz.return_value

        url = reverse("create-quiz")
        response = self.client.post(url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "Test Quiz")
        self.assertEqual(len(response.data["questions"]), 1)
        self.assertEqual(response.data["questions"][0]["question_title"], "What is 2+2?")
        self.assertEqual(response.data["questions"][0]["question_options"], ["1","2","3","4"])
        self.assertEqual(response.data["questions"][0]["answer"], "4")
