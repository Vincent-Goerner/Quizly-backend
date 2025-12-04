from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

class LogoutTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )

    def test_post_logout_successful(self):
        url = reverse('logout')
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        self.client.cookies.load({
            "access_token": access_token,
            "refresh_token": refresh_token,
        })

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        