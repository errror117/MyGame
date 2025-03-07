from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()  # Get the correct user model dynamically

class AuthenticationTests(APITestCase):
    """Test authentication API endpoints."""

    def setUp(self):
        """Create a test user before running tests."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.login_url = "http://127.0.0.1:8000/api/auth/login/"
        self.protected_url = "http://127.0.0.1:8000/api/auth/protected/"


    def test_user_login(self):
        """Test that a user can log in and receive JWT tokens."""
        response = self.client.post(self.login_url, {"username": "testuser", "password": "testpass"}, follow=True)
        
         # Debugging: Print response content
        print("Login Response Status:", response.status_code)
        print("Login Response Data:", response.json())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)  # Check if tokens are returned

    def test_protected_route_without_auth(self):
        """Test accessing a protected route without authentication."""
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_route_with_auth(self):
        """Test accessing a protected route with a valid token."""
        login_response = self.client.post(self.login_url, {"username": "testuser", "password": "testpass"}, follow=True)
        token = login_response.data["tokens"]["access"]
        headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        response = self.client.get(self.protected_url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
