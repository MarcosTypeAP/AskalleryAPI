"""Post model."""

# Django
from django.db import models

# Models
from users.models import User

# Utils
from utils.models import AskalleryModel


class Post(AskalleryModel, models.Model):
    """Post model.
    
    A Post is created by a user and it contain 
    mainly a caption and an image.
    """

    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    caption = models.TextField(
        'caption',
        max_length=400,
        help_text='It can be short description of the picture and extra info.'
    )

    image = models.ImageField(
        'picture',
        upload_to='posts/pictures/',
        help_text='Its the main content of the post.',
    )

    likes = models.ManyToManyField('users.User', related_name='likes')

    comments = models.ManyToManyField(
        'users.User',
        through='posts.Comment', 
        through_fields=('post', 'user'),
        related_name='comments'
    )

    likes_quantity = models.IntegerField(
        'quantity of likes',
        default=0, 
        help_text=(
            'Quantity of likes of this post.'
            'Stores the value to perform less queries.'
            'Increase 1 when another user give a like to this post.',
        )
    )

    comments_quantity = models.IntegerField(
        'quantity of comments',
        default=0, 
        help_text=(
            'Quantity of comments of this post.'
            'Stores the value to perform less queries.'
            'Increase 1 when another user leaves a comment on this post.',
        )
    )

    is_active = models.BooleanField(
        'active',
        default=True, 
        help_text='It will be False when the post is removed.'
    )

    def __str__(self):
        """Returns the user username
        and a short version of the caption.
        """
        return f'{self.user.username} - {self.caption[:10]}...'