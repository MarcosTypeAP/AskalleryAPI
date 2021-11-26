"""User views tests."""

# Django
from django.shortcuts import get_object_or_404

# REST Framework
from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse_lazy

# Models
from users.models import User, Profile

# Utils
from utils.tests import create_users


class UserViewsTestCase(APITestCase):
    """User views test case."""
    def setUp(self):
        self.signup_url = reverse_lazy('users:users-signup')
        self.token_pair_url = reverse_lazy('users:token_obtain_pair')
        self.token_refresh_url = reverse_lazy('users:token_refresh')
        self.signup_data = {
            'username': 'testusername',
            'email': 'email@test.com',
            'first_name': 'firstnametest',
            'last_name': 'lastnametest',
            'password': '12ThreeFour',
            'password_confirmation': '12ThreeFour',
        }
        self.users, self.user_passwords = create_users()

    def test_signup_action(self):
        """Test the creation of a new user."""
        response = self.client.post(self.signup_url, self.signup_data)

        self.assertEqual(response.status_code, 201)

        user = get_object_or_404(User, email=self.signup_data['email'])

        self.assertTrue(user.is_client)
        self.assertTrue(user.is_active)

        profile = get_object_or_404(Profile, user=user)

        self.assertEqual(profile, user.profile)

        is_logged_in = self.client.login(
            email=self.signup_data['email'],
            password=self.signup_data['password']
        )

        self.assertTrue(is_logged_in)

    def test_token_views(self):
        """Test the token creation, refresh
        and use it to authentication.
        """
        user_1, user_2, _ = self.users

        response = self.client.post(
            self.token_pair_url,
            data={
                'email': user_1.email,
                'password': self.user_passwords['u1_password']
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        response = self.client.post(
            self.token_refresh_url, data={'refresh': response.data['refresh']}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertNotIn('refresh', response.data)

        client = APIClient()
        client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + response.data['access']
        )

        follow_url = reverse_lazy('users:users-follow', args=[user_2.pk])
        response = client.post(follow_url)

        self.assertEqual(response.status_code, 201)

    def test_follow_action(self):
        """Test if be created a follow relationship
        between two users.
        """
        client_user, user_2, _ = self.users

        client = APIClient()
        client.force_authenticate(user=client_user)

        follow_url = reverse_lazy('users:users-follow', args=[user_2.pk])
        response = client.post(follow_url)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['current_user'], client_user.pk)
        self.assertEqual(response.data['followed_user'], user_2.pk)

        self.assertEqual(client_user.profile.following.count(), 1)
        self.assertEqual(client_user.profile.following.last(), user_2)
        self.assertEqual(user_2.profile.followers.count(), 1)
        self.assertEqual(user_2.profile.followers.last(), client_user)

        response = client.delete(follow_url)

        self.assertEqual(response.status_code, 204)

        self.assertEqual(client_user.profile.following.count(), 0)
        self.assertEqual(user_2.profile.followers.count(), 0)
