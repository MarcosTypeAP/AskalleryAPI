"""Post views tests."""

# REST Framework
from rest_framework.test import APITestCase, APIClient
from rest_framework.reverse import reverse_lazy

# Models
from posts.models import Post, Comment

# Utils
from PIL import Image
import tempfile
from utils.tests import create_users


class PostViewsAPITestCase(APITestCase):
    """Post views API test case."""

    def create_image(self):
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            image = Image.new('RGB', (200, 200), 'white')
            image.save(f, 'PNG')

        return open(f.name, mode='rb')

    def setUp(self):
        self.create_post_url = reverse_lazy('posts:posts-list')
        self.list_post_url = self.create_post_url
        self.users, _ = create_users()

    def test_create_post(self):
        """Verifies that the posts can be created successfully."""
        user_1, _, _ = self.users
        data = {
            'caption': 'Caption for testing 1.',
            'image': self.create_image()
        }
        c = APIClient()
        response = c.post(self.create_post_url, {})

        self.assertEqual(response.status_code, 401)

        c.force_authenticate(user=user_1)
        response = c.post(self.create_post_url, data)
        data['image'].close()

        self.assertEqual(response.status_code, 201)

        post = Post.objects.get(user=user_1)

        self.assertEqual(post.caption, data['caption'])
        self.assertIn('tmp', post.image.url)
        self.assertIn('.png', post.image.url)

    def test_list_posts(self):
        """Verifies that the posts can be retrieved."""
        user_1, user_2, _ = self.users
        data = {
            'caption': 'Caption for testing 1.',
            'image': self.create_image(),
        }
        c = APIClient()
        response = c.get(self.list_post_url)

        self.assertEqual(response.status_code, 200)

        c.force_authenticate(user=user_1)
        c.post(self.create_post_url, data)
        c.post(self.create_post_url, data)
        c.post(self.create_post_url, data)
        c.post(self.create_post_url, data)
        data['image'].close()
        response = c.get(self.list_post_url)

        self.assertEqual(response.status_code, 200)