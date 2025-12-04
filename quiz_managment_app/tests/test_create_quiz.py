from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from unittest.mock import MagicMock, patch, mock_open

import sys
import os


class CreateQuizTest(APITestCase):
    def setUp(self):
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

    @patch("quiz_managment_app.api.views.MediaQuizProcessor.fetch_audio_from_url")
    @patch("quiz_managment_app.api.views.MediaQuizProcessor.transcribe_with_whisper")
    @patch("quiz_managment_app.api.views.MediaQuizProcessor.generate_quiz_with_gemini")
    @patch("quiz_managment_app.api.views.MediaQuizProcessor.clean_output_text")
    @patch("quiz_managment_app.api.views.MediaQuizProcessor.remove_markdown_fencing")

    def test_create_quiz_success(
        self,
        mock_remove_md,
        mock_clean_text,
        mock_generate_gemini,
        mock_transcribe,
        mock_fetch_audio,
    ):
        mock_remove_md.return_value = None
        mock_clean_text.return_value = "mock quiz text"
        mock_generate_gemini.return_value = None
        mock_transcribe.return_value = None
        mock_fetch_audio.return_value = None
        
        url = reverse("create-quiz")

        response = self.client.post(url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "Test Quiz")
        self.assertEqual(len(response.data["questions"]), 1)
