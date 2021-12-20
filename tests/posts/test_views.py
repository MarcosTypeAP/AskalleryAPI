"""Post views tests."""

# REST Framework
from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse_lazy

# Django
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

# Models
from posts.models import Post, Comment

# Utils
from utils.tests import (
    create_users,
    create_data_list,
)
import os


class StaticLiveServerPostViewsTestCase(StaticLiveServerTestCase):
    """Static live server test case for post views."""

    port = os.environ.get('PORT')

    def setUp(self):
        self.create_post_url = reverse_lazy('posts:posts-list')
        self.users, _ = create_users()

    def test_create_posts(self):
        """Verifies that the posts can be created successfully."""
        user_1, _, _ = self.users
        data_list = create_data_list(1)[0]
        c1 = APIClient()
        response = c1.post(self.create_post_url, {})

        self.assertEqual(response.status_code, 401)

        c1.force_authenticate(user=user_1)
        response = c1.post(self.create_post_url, {})

        self.assertEqual(response.status_code, 403)

        user_1.is_verified = True
        user_1.save()
        response = c1.post(self.create_post_url, data_list)
        data_list['image'].close()
        import pdb; pdb.set_trace()

        self.assertEqual(response.status_code, 201)

        post = Post.objects.get(user=user_1)

        self.assertEqual(post.caption, data_list['caption'])
        self.assertIn('tmp', post.image.url)
        self.assertIn('.png', post.image.url)


class PostViewsAPITestCase(APITestCase):
    """Post views API test case."""
    def setUp(self):
        self.create_post_url = reverse_lazy('posts:posts-list')
        self.list_post_url = self.create_post_url
        self.like_post_url = reverse_lazy('posts:posts-like')
        self.users, _ = create_users()

    def test_list_posts(self):
        """Verifies that all the posts can be listed."""
        user_1, _, _ = self.users
        c = APIClient()
        response = c.get(self.list_post_url)

        self.assertEqual(response.status_code, 401)

        c.force_authenticate(user=user_1)
        Post.objects.create(user=user_1)
        Post.objects.create(user=user_1)
        Post.objects.create(user=user_1)

        response = c.get(self.list_post_url)

        self.assertEqual(response.status_code, 403)

        user_1.is_verified = True
        user_1.save()
        response = c.get(self.list_post_url)

        self.assertEqual(response.status_code, 200)

        response = response.json()

        self.assertEqual(len(response['results']), 3)
        self.assertEqual(response['count'], 3)

        post_1 = Post.objects.get(pk=1)
        post_1.is_active = False
        post_1.save()

        response = c.get(self.list_post_url)

        self.assertEqual(response.status_code, 200)

        response = response.json()

        self.assertEqual(len(response['results']), 2)
        self.assertEqual(response['count'], 2)

    def test_retrieve_post(self):
        """Verifies that a post can be retrieved."""
        user_1, _, _ = self.users
        c1 = APIClient()
        retrieve_post_url = reverse_lazy('posts:posts-detail', args=[99])
        response = c1.get(retrieve_post_url)

        self.assertEqual(response.status_code, 404)

        post = Post.objects.create(user=user_1)
        Post.objects.create(user=user_1)

        retrieve_post_url = reverse_lazy('posts:posts-detail', args=[post.pk])
        response = c1.get(retrieve_post_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['pk'], post.pk)

    def test_update_post(self):
        """Verifies that the post's 'caption' attribute
        can be updated.
        """
        user_1, user_2, _ = self.users
        c1 = APIClient()
        c2 = APIClient()
        partial_update_data = {'caption': 'New test caption'}
        update_post_url = reverse_lazy('posts:posts-detail', args=[99])
        response = c1.patch(update_post_url, data=partial_update_data)

        self.assertEqual(response.status_code, 401)

        c1.force_authenticate(user=user_1)
        c2.force_authenticate(user=user_2)
        response = c1.patch(update_post_url, data=partial_update_data)

        self.assertEqual(response.status_code, 403)

        user_1.is_verified = True
        user_1.save()
        response = c1.patch(update_post_url, data=partial_update_data)

        self.assertEqual(response.status_code, 404)

        post = Post.objects.create(user=user_1, caption='Test caption')
        update_post_url = reverse_lazy('posts:posts-detail', args=[post.pk])
        response = c1.patch(update_post_url, data=partial_update_data)
        post = Post.objects.get(pk=post.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(post.caption, partial_update_data['caption'])

        post.caption = 'Test caption'
        post.save()
        response = c1.put(update_post_url, data=partial_update_data)
        post = Post.objects.get(pk=post.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(post.caption, partial_update_data['caption'])

        user_2.is_verified = True
        user_2.save()
        response = c2.patch(update_post_url, data=partial_update_data)

        self.assertEqual(response.status_code, 403)

        post.is_active = False
        post.save()
        response = c1.patch(update_post_url, data=partial_update_data)

        self.assertEqual(response.status_code, 404)

    def test_destroy_posts(self):
        """Verifies that a post can be destroyed."""
        user_1, user_2, _ = self.users
        c1 = APIClient()
        c2 = APIClient()
        delete_post_url = reverse_lazy('posts:posts-detail', args=[99])
        response = c1.delete(delete_post_url)

        self.assertEqual(response.status_code, 401)

        c1.force_authenticate(user=user_1)
        c2.force_authenticate(user=user_2)
        response = c1.delete(delete_post_url)

        self.assertEqual(response.status_code, 403)

        user_1.is_verified = True
        user_1.save()
        response = c1.delete(delete_post_url)

        self.assertEqual(response.status_code, 404)

        post = Post.objects.create(user=user_1)
        post.is_active = False
        post.save()
        delete_post_url = reverse_lazy('posts:posts-detail', args=[post.pk])
        response = c1.delete(delete_post_url)

        self.assertEqual(response.status_code, 404)

        post.is_active = True
        post.save()
        user_2.is_verified = True
        user_2.save()
        response = c2.delete(delete_post_url)

        self.assertEqual(response.status_code, 403)

        response = c1.delete(delete_post_url)
        post = Post.objects.get(pk=post.pk)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(post.is_active, False)
        self.assertFalse(Post.objects.filter(is_active=True).exists())

    def test_like_post(self):
        """Verifies that a post can be liked and unliked."""
        user_1, user_2, _ = self.users
        c1 = APIClient()
        c2 = APIClient()
        like_post_c1_url = reverse_lazy('posts:posts-like', args=[1])
        response = c1.post(like_post_c1_url)

        self.assertEqual(response.status_code, 401)

        c1.force_authenticate(user=user_1)
        c2.force_authenticate(user=user_2)
        post = Post.objects.create(user=user_1)
        like_post_c1_url = reverse_lazy('posts:posts-like', args=[post.pk])
        response = c1.post(like_post_c1_url)

        self.assertEqual(response.status_code, 403)

        user_1.is_verified = True
        user_1.save()
        user_2.is_verified = True
        user_2.save()
        response = c1.post(like_post_c1_url)

        self.assertEqual(response.status_code, 201)

        response = c2.post(like_post_c1_url)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(post.likes.count(), 2)
        self.assertTrue(post.likes.filter(pk=user_1.pk).exists())
        self.assertTrue(post.likes.filter(pk=user_2.pk).exists())

        response = c1.delete(like_post_c1_url)

        self.assertEqual(response.status_code, 204)

        response = c2.delete(like_post_c1_url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(post.likes.count(), 0)
        self.assertFalse(post.likes.filter(pk=user_1.pk).exists())
        self.assertFalse(post.likes.filter(pk=user_2.pk).exists())

        post.is_active = False
        post.save()
        response = c1.post(like_post_c1_url)

        self.assertEqual(response.status_code, 404)

        like_post_c1_url = reverse_lazy('posts:posts-like', args=[99])
        response = c1.post(like_post_c1_url)

        self.assertEqual(response.status_code, 404)

    def test_list_liked_posts(self):
        """Verify that the posts
        liked by a user can be listed.
        """
        user_1, _, _ = self.users
        c1 = APIClient()
        post_1 = Post.objects.create(user=user_1)
        post_2 = Post.objects.create(user=user_1)
        post_3 = Post.objects.create(user=user_1)
        Post.objects.create(user=user_1)
        post_5 = Post.objects.create(user=user_1)
        post_1.add_like(user_1)
        post_2.add_like(user_1)
        post_3.add_like(user_1)
        post_5.add_like(user_1)
        list_liked_posts_url = reverse_lazy('posts:posts-liked')
        response = c1.get(list_liked_posts_url)

        self.assertEqual(response.status_code, 401)

        c1.force_authenticate(user=user_1)
        response = c1.get(list_liked_posts_url)

        self.assertEqual(response.status_code, 403)

        user_1.is_verified = True
        user_1.save()
        response = c1.get(list_liked_posts_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 4)
        for post in response.json()['results']:
            self.assertIn(
                post['pk'], [post_1.pk, post_2.pk, post_3.pk, post_5.pk]
            )

    def test_comment_post(self):
        user_1, user_2, _ = self.users
        c1 = APIClient()
        c2 = APIClient()
        post = Post.objects.create(user=user_1)
        comment_post_url = reverse_lazy('posts:comments-list')
        response = c1.post(comment_post_url)

        self.assertEqual(response.status_code, 401)

        c1.force_authenticate(user=user_1)
        data = {'content': 'Test comment content', 'post': 99}
        response = c1.post(comment_post_url, data=data, format='json')

        self.assertEqual(response.status_code, 403)

        user_1.is_verified = True
        user_1.save()
        user_2.is_verified = True
        user_2.save()
        response = c1.post(comment_post_url, data=data, format='json')

        self.assertEqual(response.status_code, 404)

        data['post'] = post.pk
        response = c1.post(comment_post_url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertTrue(post.comment_set.filter(user=user_1).exists())
        self.assertEqual(post.comment_set.count(), 1)

        c2.force_authenticate(user=user_2)
        response = c2.post(comment_post_url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertTrue(post.comment_set.filter(user=user_2).exists())
        self.assertEqual(post.comment_set.count(), 2)

        comment_c1 = Comment.objects.get(user=user_1)
        uncomment_post_url = reverse_lazy(
            'posts:comments-detail', args=(comment_c1.pk, )
        )
        response = c2.delete(uncomment_post_url)

        self.assertEqual(response.status_code, 403)

        response = c1.delete(uncomment_post_url)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(post.comment_set.filter(user=user_1).exists())
        self.assertEqual(post.comment_set.count(), 1)

        comment_c2 = Comment.objects.get(user=user_2)
        uncomment_post_url = reverse_lazy(
            'posts:comments-detail', args=(comment_c2.pk, )
        )
        response = c1.delete(uncomment_post_url)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(post.comment_set.filter(user=user_2).exists())
        self.assertEqual(post.comment_set.count(), 0)

        post.is_active = False
        post.save()
        response = c1.delete(uncomment_post_url)

        self.assertEqual(response.status_code, 404)

        response = c1.post(comment_post_url, data=data, format='json')

        self.assertEqual(response.status_code, 404)

    def test_list_post_comments(self):
        """Verifies that post's comments can be listed."""
        user_1, _, _ = self.users
        c1 = APIClient()
        list_post_comments_url = reverse_lazy(
            'posts:posts-comments', args=[99]
        )
        response = c1.get(list_post_comments_url)

        self.assertEqual(response.status_code, 401)

        c1.force_authenticate(user=user_1)
        response = c1.get(list_post_comments_url)

        self.assertEqual(response.status_code, 403)

        user_1.is_verified = True
        user_1.save()
        post_1 = Post.objects.create(user=user_1)
        post_2 = Post.objects.create(user=user_1)
        comment_1 = Comment.objects.create(user=user_1, post=post_1)
        comment_2 = Comment.objects.create(user=user_1, post=post_1)
        Comment.objects.create(user=user_1, post=post_2)
        list_post_comments_url = reverse_lazy(
            'posts:posts-comments', args=[post_1.pk]
        )
        response = c1.get(list_post_comments_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 2)
        self.assertEqual(response.json()['count'], 2)
        for comment in response.json()['results']:
            self.assertIn(comment['pk'], [comment_1.pk, comment_2.pk])

    def test_like_comment(self):
        """Verifies that a comment can be liked and unliked."""
        user_1, user_2, _ = self.users
        c1 = APIClient()
        c2 = APIClient()
        like_comment_c1_url = reverse_lazy('posts:comments-like', args=[99])
        response = c1.post(like_comment_c1_url)

        self.assertEqual(response.status_code, 401)

        c1.force_authenticate(user=user_1)
        c2.force_authenticate(user=user_2)
        response = c1.post(like_comment_c1_url)

        self.assertEqual(response.status_code, 403)

        user_1.is_verified = True
        user_1.save()
        user_2.is_verified = True
        user_2.save()
        response = c1.post(like_comment_c1_url)

        self.assertEqual(response.status_code, 404)

        post = Post.objects.create(user=user_1)
        comment = Comment.objects.create(user=user_1, post=post)
        like_comment_c1_url = reverse_lazy(
            'posts:comments-like', args=[comment.pk]
        )
        response = c1.post(like_comment_c1_url)

        self.assertEqual(response.status_code, 201)

        response = c2.post(like_comment_c1_url)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.likes.count(), 2)
        self.assertTrue(comment.likes.filter(pk=user_1.pk).exists())
        self.assertTrue(comment.likes.filter(pk=user_2.pk).exists())

        response = c1.delete(like_comment_c1_url)

        self.assertEqual(response.status_code, 204)

        response = c2.delete(like_comment_c1_url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(comment.likes.count(), 0)
        self.assertFalse(comment.likes.filter(pk=user_1.pk).exists())
        self.assertFalse(comment.likes.filter(pk=user_2.pk).exists())

        post.is_active = False
        post.save()
        response = c1.post(like_comment_c1_url)

        self.assertEqual(response.status_code, 404)

        response = c2.delete(like_comment_c1_url)

        self.assertEqual(response.status_code, 404)
