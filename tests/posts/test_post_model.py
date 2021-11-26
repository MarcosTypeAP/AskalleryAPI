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
        relationship between the post and a user.
        """
        user_1, user_2, _ = self.users

        post = Post.objects.create(user=user_1)
        post.add_like(user_1)
        post.add_like(user_1)
        post.add_like(user_2)
        post.add_like(user_2)
        post.add_like(user_2)

        self.assertEqual(post.likes.count(), 2)
        self.assertEqual(post.likes_quantity, 2)
        self.assertTrue(post.likes.filter(pk=user_1.pk).exists())
        self.assertTrue(post.likes.filter(pk=user_2.pk).exists())

    def test_remove_like(self):
        """Verifies that 'remove_like' method can remove the 'like'
        relationship between the post and a user.
        """
        user_1, user_2, _ = self.users

        post = Post.objects.create(user=user_1)
        post.likes.add(user_1)
        post.likes.add(user_2)
        post.likes_quantity = 2

        post.remove_like(user_1)
        post.remove_like(user_1)
        post.remove_like(user_1)
        post.remove_like(user_2)

        self.assertEqual(post.likes.count(), 0)
        self.assertEqual(post.likes_quantity, 0)
        self.assertFalse(post.likes.filter(pk=user_1.pk).exists())
        self.assertFalse(post.likes.filter(pk=user_2.pk).exists())

    def test_add_comment(self):
        user_1, user_2, _ = self.users
        CONTENT = 'Test comment content'
        post = Post.objects.create(user=user_1)
        post.add_comment(user_1, CONTENT)
        post.add_comment(user_1, CONTENT)
        post.add_comment(user_2, CONTENT)
        post.add_comment(user_2, CONTENT)

        self.assertEqual(post.comment_set.count(), 4)
        self.assertEqual(post.comments_quantity, 4)
        self.assertTrue(post.comment_set.filter(user=user_1).exists())
        self.assertTrue(post.comment_set.filter(user=user_2).exists())
        self.assertEqual(post.comment_set.first().content, CONTENT)

        self.assertEqual(Comment.objects.filter(user=user_1).count(), 2)
        self.assertEqual(Comment.objects.filter(user=user_2).count(), 2)

    def test_remove_comment(self):
        user_1, user_2, _ = self.users
        CONTENT = 'Test comment content'
        post = Post.objects.create(user=user_1)
        co_1 = Comment.objects.create(user=user_1, post=post, content=CONTENT)
        co_2 = Comment.objects.create(user=user_1, post=post, content=CONTENT)
        co_3 = Comment.objects.create(user=user_2, post=post, content=CONTENT)
        Comment.objects.create(user=user_2, post=post, content=CONTENT)
        post.comments_quantity = 4
        post.save()

        post.remove_comment(co_1.pk)
        post.remove_comment(co_2.pk)
        post.remove_comment(co_3.pk)

        self.assertEqual(post.comment_set.count(), 1)
        self.assertEqual(post.comments_quantity, 1)
        self.assertFalse(post.comment_set.filter(user__pk=user_1.pk).exists())
        self.assertTrue(post.comment_set.filter(user__pk=user_2.pk).exists())

        self.assertFalse(Comment.objects.filter(user=user_1).exists())
        self.assertEqual(Comment.objects.filter(user=user_2).count(), 1)
