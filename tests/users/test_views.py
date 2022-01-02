"""User views tests."""

# Django
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core import mail

# REST Framework
from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse_lazy

# Models
from users.models import User, Profile
from posts.models import Post

# Utils
from utils.tests import (
    create_users,
)
import jwt
from utils.serializers import gen_verification_token


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

    def test_signup(self):
        """Test the creation of a new user and
        if it receives a verification email with a token.
        """
        c1 = APIClient()
        response = c1.post(self.signup_url, self.signup_data)

        self.assertEqual(response.status_code, 201)

        user = User.objects.get(email=self.signup_data['email'])

        self.assertTrue(user.is_client)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_verified)
        self.assertTrue(user.profile is not None)

        is_logged_in = c1.login(
            email=self.signup_data['email'],
            password=self.signup_data['password']
        )

        self.assertTrue(is_logged_in)

        self.assertEqual(len(mail.outbox), 1)

        email_lines = mail.outbox[0].body.splitlines()
        verify_url = str(reverse_lazy('users:users-verify'))
        raw_email_verify_url = [l for l in email_lines if verify_url in l][-1]
        token = raw_email_verify_url.split('?token=')[-1]
        payload = jwt.decode(token, settings.SECRET_KEY, 'HS256')

        self.assertEqual(payload['user'], user.username)
        self.assertEqual(payload['type'], 'email_confirmation')

    def test_verify(self):
        """Verifies that a user can verify its account."""
        user_1, _, _ = self.users
        user_1.is_verified = False
        user_1.save()
        c1 = APIClient()
        token = gen_verification_token(user_1)
        verify_url = '{}?token={}'.format(
            reverse_lazy('users:users-verify'),
            token
        )
        response = c1.get(verify_url)
        user_1 = User.objects.get(pk=user_1.pk)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(user_1.is_verified)

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
        user_1.is_verified = True
        user_1.save()
        user_2.is_verified = True
        user_2.save()
        response = client.post(follow_url)

        self.assertEqual(response.status_code, 201)

    def test_retrieve_user(self):
        """Verifies that a user can be retrieved."""
        user_1, _, _ = self.users
        c1 = APIClient()
        retrieve_user_url = reverse_lazy('users:users-detail', args=[99])
        response = c1.get(retrieve_user_url)

        self.assertEqual(response.status_code, 404)

        retrieve_user_url = reverse_lazy(
            'users:users-detail', args=[user_1.pk]
        )
        response = c1.get(retrieve_user_url)

        self.assertEqual(response.status_code, 404)

        user_1.is_verified = True
        user_1.save()
        response = c1.get(retrieve_user_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['pk'], user_1.pk)

    def test_list_users(self):
        """Verifies that users can be listed and searched."""
        user_1, user_2, user_3 = self.users
        c1 = APIClient()
        list_users_url = reverse_lazy('users:users-list')
        response = c1.get(list_users_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 0)

        user_1.is_verified = True
        user_1.save()
        user_2.is_verified = True
        user_2.save()
        user_3.is_verified = True
        user_3.save()
        response = c1.get(list_users_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 3)

        search_user_url = '{}?search={}'.format(
            list_users_url, user_2.username[:5]
        )
        response = c1.get(search_user_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['pk'], user_2.pk)

    def test_follow(self):
        """Test if be created a follow relationship
        between two users.
        """
        client_user, user_2, _ = self.users
        client = APIClient()
        follow_url = reverse_lazy('users:users-follow', args=[user_2.pk])
        response = client.post(follow_url)

        self.assertEqual(response.status_code, 401)

        client.force_authenticate(user=client_user)
        response = client.post(follow_url)

        self.assertEqual(response.status_code, 403)

        client_user.is_verified = True
        client_user.save()
        user_2.is_verified = True
        user_2.save()
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

    def test_update_profile(self):
        """Verifies that a profile can be updated."""
        user_1, _, _ = self.users
        partial_update_data = {'biography': 'test biography 1'}
        c1 = APIClient()
        update_profile_url = reverse_lazy('users:users-profile')
        response = c1.patch(update_profile_url)

        self.assertEqual(response.status_code, 401)

        c1.force_authenticate(user=user_1)
        response = c1.patch(update_profile_url, data=partial_update_data)

        self.assertEqual(response.status_code, 403)

        user_1.is_verified = True
        user_1.save()
        response = c1.patch(update_profile_url, data=partial_update_data)

        self.assertEqual(response.status_code, 201)

        profile = Profile.objects.get(user=user_1, pk=1)

        self.assertEqual(profile.biography, partial_update_data['biography'])

    def test_list_followers(self):
        """Verifies that all followers of a user
        can be listed.
        """
        user_1, user_2, user_3 = self.users
        c1, c2, c3 = APIClient(), APIClient(), APIClient()
        list_user_followers_url = reverse_lazy(
            'users:users-followers', args=[99]
        )
        response = c1.get(list_user_followers_url)

        self.assertEqual(response.status_code, 401)

        c1.force_authenticate(user=user_1)
        c2.force_authenticate(user=user_2)
        c3.force_authenticate(user=user_3)
        response = c1.get(list_user_followers_url)

        self.assertEqual(response.status_code, 403)

        user_1.is_verified = True
        user_1.save()
        user_2.is_verified = True
        user_2.save()
        user_3.is_verified = True
        user_3.save()
        response = c1.get(list_user_followers_url)

        self.assertEqual(response.status_code, 404)

        user_2.profile.start_follow(user_1)
        user_3.profile.start_follow(user_1)
        list_user_followers_url = reverse_lazy(
            'users:users-followers', args=[user_1.pk]
        )
        response = c2.get(list_user_followers_url)

        self.assertEqual(response.status_code, 200)

        response = response.json()

        self.assertEqual(len(response['results']), 2)
        self.assertIn(response['results'][0]['pk'], [user_2.pk, user_3.pk])
        self.assertIn(response['results'][1]['pk'], [user_2.pk, user_3.pk])

        user_3.profile.stop_following(user_1)
        response = c2.get(list_user_followers_url)

        self.assertEqual(response.status_code, 200)

        response = response.json()

        self.assertEqual(len(response['results']), 1)
        self.assertEqual(response['results'][0]['pk'], user_2.pk)

    def test_list_following(self):
        """Verifies that all followers of a user
        can be listed.
        """
        user_1, user_2, user_3 = self.users
        c1, c2, c3 = APIClient(), APIClient(), APIClient()
        list_user_following_url = reverse_lazy(
            'users:users-following', args=[99]
        )
        response = c1.get(list_user_following_url)

        self.assertEqual(response.status_code, 401)

        c1.force_authenticate(user=user_1)
        c2.force_authenticate(user=user_2)
        c3.force_authenticate(user=user_3)
        response = c1.get(list_user_following_url)

        self.assertEqual(response.status_code, 403)

        user_1.is_verified = True
        user_1.save()
        user_2.is_verified = True
        user_2.save()
        user_3.is_verified = True
        user_3.save()
        response = c1.get(list_user_following_url)

        self.assertEqual(response.status_code, 404)

        user_1.profile.start_follow(user_2)
        user_1.profile.start_follow(user_3)
        list_user_following_url = reverse_lazy(
            'users:users-following', args=[user_1.pk]
        )
        response = c2.get(list_user_following_url)

        self.assertEqual(response.status_code, 200)

        response = response.json()

        self.assertEqual(len(response['results']), 2)
        self.assertIn(response['results'][0]['pk'], [user_2.pk, user_3.pk])
        self.assertIn(response['results'][1]['pk'], [user_2.pk, user_3.pk])

        user_1.profile.stop_following(user_3)
        response = c2.get(list_user_following_url)

        self.assertEqual(response.status_code, 200)

        response = response.json()

        self.assertEqual(len(response['results']), 1)
        self.assertEqual(response['results'][0]['pk'], user_2.pk)

    def test_list_user_posts(self):
        """Verify that only the posts with
        the given user id will be listed."""
        user_1, user_2, _ = self.users
        c1 = APIClient()
        list_user_1_posts_url = reverse_lazy(
            "users:users-posts", args=(user_1.pk, )
        )
        list_user_2_posts_url = reverse_lazy(
            "users:users-posts", args=(user_2.pk, )
        )
        Post.objects.create(user=user_1)
        Post.objects.create(user=user_1)
        Post.objects.create(user=user_1)
        Post.objects.create(user=user_2)
        Post.objects.create(user=user_2)
        Post.objects.create(user=user_2)

        response = c1.get(list_user_1_posts_url)

        self.assertEqual(response.status_code, 200)

        response = response.json()

        self.assertEqual(response["count"], 3)
        for p in response["results"]:
            self.assertEqual(p["user"]["pk"], user_1.pk)

        response = c1.get(list_user_2_posts_url)

        self.assertEqual(response.status_code, 200)

        response = response.json()

        self.assertEqual(response["count"], 3)
        for p in response["results"]:
            self.assertEqual(p["user"]["pk"], user_2.pk)

        post_1 = Post.objects.get(pk=1)
        post_1.is_active = False
        post_1.save()
        response = c1.get(list_user_1_posts_url)

        self.assertEqual(response.status_code, 200)

        response = response.json()

        self.assertEqual(response["count"], 2)
