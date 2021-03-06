from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
UPDATE_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """
    Test the USERS API (public)
    """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """
        Test creating user with valid payload is successful
        """
        payload = {
            'email': 'test@dev.com',
            'password': 'Testpassword123',
            'name': "test Name"
        }
        resp = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**resp.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', resp.data)

    def test_user_exists(self):
        """
        Test creating user that already exists fails
        """
        payload = {
            'email': 'test@dev.com',
            'password': 'testpass'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_to_short(self):
        """
        Test that the password must be more than 5 characters
        """
        payload = {
            'email': 'test@example.com',
            'password': 'pw'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """
        Test that the token is created for the user
        """
        payload = {
            'email': 'test@dev.com',
            'password': 'testPassword123'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """
        Test that token is not created if invalid credentials are given
        """
        payload = {
            'email': 'test@email.com',
            'password': 'Testpassword123'
        }
        create_user(**payload)
        payload['password'] = '123'
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """
        Test that token is not created if user doesn't exist
        """
        payload = {'email': 'test@dev.com', 'password': 'testpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_misssing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(UPDATE_URL)

        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """
    Tests API requests that require authentication
    """
    def setUp(self):
        self.user = create_user(
            email='test@dev.com',
            password='testpass',
            name='test'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """
        Test retrieving profile for logged in user
        """
        res = self.client.get(UPDATE_URL)
        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """
        Test that post is not allowed on update enpoint
        """
        res = self.client.post(UPDATE_URL, {})
        self.assertEquals(res.status_code,
                          status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """
        Test updating the user profile for authenticated user
        """
        payload = {
            'name': 'new name',
            'password': 'newpass123'
        }
        res = self.client.patch(UPDATE_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEquals(res.status_code, status.HTTP_200_OK)
