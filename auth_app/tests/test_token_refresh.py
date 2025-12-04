from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class CookieTokenRefreshTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)
        self.access_token = str(refresh.access_token)
    
    def test_post_refresh_token_successful(self):
        url = reverse('token_refresh')
        
        self.client.cookies.load({"refresh_token": self.refresh_token})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("access", response.data)
        self.assertIn("access_token", response.cookies)
        self.assertEqual(response.cookies["access_token"].value, response.data["access"])
    
    def test_post_refresh_token_missing(self):
        url = reverse('token_refresh')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_refresh_token_invalid(self):
        url = reverse('token_refresh')
        self.client.cookies["refresh_token"] = "invalidtoken"

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)