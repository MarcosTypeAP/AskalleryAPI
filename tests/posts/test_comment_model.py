"""Post model tests."""

# Django
from django.test import TestCase

# Models
from posts.models import Post, Comment

# Utils
from utils.tests import create_users


class PostModelTestCase(TestCase):
    """Post model test case."""

    def setUp(self):
        self.users, _ = create_users()

    def test_add_like(self):
        """Verifies that 'add_like' method can add a 'like'
        relationship between the comment and a user.
        """
        user_1, user_2, _ = self.users

        post = Post.objects.create(user=user_1)
        comment = Comment.objects.create(user=user_1, post=post)
        comment.add_like(user_1)
        comment.add_like(user_1)
        comment.add_like(user_2)
        comment.add_like(user_2)
        comment.add_like(user_2)

        self.assertEqual(comment.likes.count(), 2)
        self.assertEqual(comment.likes_quantity, 2)
        self.assertTrue(comment.likes.filter(pk=user_1.pk).exists())
        self.assertTrue(comment.likes.filter(pk=user_2.pk).exists())

    def test_remove_like(self):
        """Verifies that 'remove_like' method can remove the 'like'
        relationship between the comment and a user.
        """
        user_1, user_2, _ = self.users

        post = Post.objects.create(user=user_1)
        comment = Comment.objects.create(user=user_1, post=post)
        comment.likes.add(user_1)
        comment.likes.add(user_2)
        comment.likes_quantity = 2

        comment.remove_like(user_1)
        comment.remove_like(user_1)
        comment.remove_like(user_1)
        comment.remove_like(user_2)

        self.assertEqual(comment.likes.count(), 0)
        self.assertEqual(comment.likes_quantity, 0)
        self.assertFalse(comment.likes.filter(pk=user_1.pk).exists())
        self.assertFalse(comment.likes.filter(pk=user_2.pk).exists())
