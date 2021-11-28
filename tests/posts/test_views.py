"""Post views tests."""

# REST Framework
from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse_lazy

# Models
from posts.models import Post, Comment

# Utils
from utils.tests import (
    create_users,
    create_data_list,
)


class PostViewsAPITestCase(APITestCase):
    """Post views API test case."""
    def setUp(self):
        self.create_post_url = reverse_lazy('posts:posts-list')
        self.list_post_url = self.create_post_url
        self.like_post_url = reverse_lazy('posts:posts-like')
        self.users, _ = create_users()

    def test_create_post(self):
        """Verifies that the posts can be created successfully."""
        user_1, _, _ = self.users
        data_list = create_data_list(1)
        c = APIClient()
        response = c.post(self.create_post_url, {})

        self.assertEqual(response.status_code, 401)

        c.force_authenticate(user=user_1)
        response = c.post(self.create_post_url, data_list[0])
        data_list[0]['image'].close()

        self.assertEqual(response.status_code, 201)

        post = Post.objects.get(user=user_1)

        self.assertEqual(post.caption, data_list[0]['caption'])
        self.assertIn('tmp', post.image.url)
        self.assertIn('.png', post.image.url)

    def test_list_posts(self):
        """Verifies that all the posts can be listed."""
        user_1, _, _ = self.users
        data_list = create_data_list(3)
        c = APIClient()
        response = c.get(self.list_post_url)

        self.assertEqual(response.status_code, 200)

        c.force_authenticate(user=user_1)
        c.post(self.create_post_url, data_list[0])
        c.post(self.create_post_url, data_list[1])
        c.post(self.create_post_url, data_list[2])
        data_list[0]['image'].close()
        data_list[1]['image'].close()
        data_list[2]['image'].close()

        response = c.get(self.list_post_url)

        self.assertEqual(response.status_code, 200)

        response = response.json()

        self.assertEqual(len(response['results']), 3)
        self.assertEqual(response['count'], 3)

    def test_retrieve_posts(self):
        """Verify that only the posts with
        the given user id will be listed."""
        user_1, user_2, _ = self.users
        user_1_post_detail_url = reverse_lazy(
            "posts:posts-detail", args=(user_1.pk, )
        )
        user_2_post_detail_url = reverse_lazy(
            "posts:posts-detail", args=(user_2.pk, )
        )
        response = self.client.get(user_1_post_detail_url)

        self.assertEqual(response.status_code, 200)

        c1 = APIClient()
        c2 = APIClient()
        data_list_1 = create_data_list(3)
        data_list_2 = create_data_list(3)
        c1.force_authenticate(user=user_1)
        c2.force_authenticate(user=user_2)

        c1.post(self.create_post_url, data_list_1[0])
        c1.post(self.create_post_url, data_list_1[1])
        c1.post(self.create_post_url, data_list_1[2])
        data_list_1[0]["image"].close()
        data_list_1[1]["image"].close()
        data_list_1[2]["image"].close()

        c2.post(self.create_post_url, data_list_2[0])
        c2.post(self.create_post_url, data_list_2[1])
        c2.post(self.create_post_url, data_list_2[2])
        data_list_2[0]["image"].close()
        data_list_2[1]["image"].close()
        data_list_2[2]["image"].close()

        response = c1.get(user_1_post_detail_url)

        self.assertEqual(response.status_code, 200)

        response = response.json()

        self.assertEqual(response["count"], 3)
        for p in response["results"]:
            self.assertEqual(p["user"]["pk"], user_1.pk)

        response = c1.get(user_2_post_detail_url)

        self.assertEqual(response.status_code, 200)

        response = response.json()

        self.assertEqual(response["count"], 3)
        for p in response["results"]:
            self.assertEqual(p["user"]["pk"], user_2.pk)

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

        like_post_c1_url = reverse_lazy('posts:posts-like', args=[99])
        response = c1.post(like_post_c1_url)

        self.assertEqual(response.status_code, 404)

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
            'posts:comments-detail',
            args=(comment_c1.pk, )
        )
        response = c2.delete(uncomment_post_url)

        self.assertEqual(response.status_code, 403)

        response = c1.delete(uncomment_post_url)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(post.comment_set.filter(user=user_1).exists())
        self.assertEqual(post.comment_set.count(), 1)

        comment_c2 = Comment.objects.get(user=user_2)
        uncomment_post_url = reverse_lazy(
            'posts:comments-detail',
            args=(comment_c2.pk, )
        )
        response = c1.delete(uncomment_post_url)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(post.comment_set.filter(user=user_2).exists())
        self.assertEqual(post.comment_set.count(), 0)
