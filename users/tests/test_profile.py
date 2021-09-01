"""User profile tests."""

# Django
from django.test import TestCase

# Models
from users.models import Profile, User

# Utils
from utils.tests import create_users


class UserProfileModelTestCase(TestCase):
    """User profile model test case."""

    def setUp(self):
        """Create new users for testing."""
        self.users = create_users()

    def test_profile_follow_methods(self):
        """Test 'start_follow' and
        'stop_following' methods.
        """
        user_1, user_2, user_3 = self.users
        
        user_1.profile.start_follow(user_2)
        user_1.profile.start_follow(user_3)

        self.assertIn(user_3, user_1.profile.following.all())
        self.assertIn(user_2, user_1.profile.following.all())

        self.assertEqual(user_1.profile.following_quantity, 2)

        self.assertEqual(user_2.profile.followers.last(), user_1)
        self.assertEqual(user_3.profile.followers.last(), user_1)

        self.assertEqual(user_2.profile.followers_quantity, 1)
        self.assertEqual(user_3.profile.followers_quantity, 1)

        user_1.profile.stop_following(user_2)
        user_1.profile.stop_following(user_3)

        self.assertEqual(user_1.profile.following.count(), 0)

        self.assertEqual(user_1.profile.following_quantity, 0)

        self.assertEqual(user_2.profile.followers.count(), 0)
        self.assertEqual(user_3.profile.followers.count(), 0)
 
        self.assertEqual(user_2.profile.followers_quantity, 0)
        self.assertEqual(user_3.profile.followers_quantity, 0)
