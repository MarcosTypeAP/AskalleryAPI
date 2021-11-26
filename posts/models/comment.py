"""Post comment model."""

# Django
from django.db import models

# Models
from posts.models import Post
from users.models import User

# Utils
from utils.models import AskalleryModel


class Comment(AskalleryModel, models.Model):
    """Comment model.

    It's text which will be related between 
    a post and an user.
    """

    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    content = models.TextField(
        'content',
        max_length=500,
        help_text='It is text given by a user.'
    )

    def __str__(self):
        """Returns the user username 
        and the post pk.
        """
        return f'{self.user.username} - PID:{self.pk}'
