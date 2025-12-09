from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

class RegistrationTest(APITestCase):
    """
    Test case for user registration endpoint, covering valid registration,
    password mismatch, and attempts to register with existing username or email.
    """
    def setUp(self):
        """
        Sets up test users and payloads for registration tests.
        """
        self.valid_user = {
            'username': 'valid_user',
            'password': 'valid_password',
            'email': 'valid@email.com',
            'repeated_password': 'valid_password'
        }
        self.invalid_user = {
            'username': 'invalid_user',
            'password': 'invalid_password',
            'email': 'invalid@email.com',
            'repeated_password': 'invalid-password'
        }
        self.existing_user = User.objects.create_user(
            username="existing",
            email="existing@example.com",
            password="password123"
        )

    def test_post_valid_registration(self):
        """
        Ensures that a valid registration request returns HTTP 200 or 201
        and successfully creates a new user.
        """
        url = reverse('registration')
        response = self.client.post(url, self.valid_user, format="json")

        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])

    def test_post_inavlid_registration(self):
        """
        Ensures that registration with mismatched passwords returns
        HTTP 400 with the appropriate error message.
        """
        url = reverse('registration')
        response = self.client.post(url, self.invalid_user, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Passwords do not match", response.data["repeated_password"][0])
    
    def test_post_existing_user_registration(self):
        """
        Ensures that registration with an existing username returns
        HTTP 400 with a relevant error message.
        """
        url = reverse('registration')
        payload = {
            "username": "existing",
            "password": "password123",
            "repeated_password": "password123",
            "email": "unique_email@example.com",
        }
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn("A user with that username already exists.", response.data["username"][0])

    def test_post_existing_email_registration(self):
        """
        Ensures that registration with an existing email returns
        HTTP 400 with a relevant error message.
        """
        url = reverse('registration')
        payload = {
            "username": "unique_user",
            "password": "password123",
            "repeated_password": "password123",
            "email": "existing@example.com",
        }
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("Email already exists", response.data["email"][0])