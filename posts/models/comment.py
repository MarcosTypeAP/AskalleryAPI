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

    likes = models.ManyToManyField('users.User', related_name='comment_likes')

    likes_quantity = models.IntegerField(
        'quantity of likes',
        default=0,
        help_text=(
            'Quantity of likes of this comment.'
            'Stores the value to perform less queries.'
            'Increase 1 when another user give a like to this comment.',
        )
    )

    def add_like(self, user):
        """Establishes a 'like' relationship between this comment and
        passed user, also updates this comment's 'likes_quantity' attribute.
        """
        if not self.likes.filter(pk=user.pk).exists():
            self.likes.add(user)
            self.likes_quantity += 1
            self.save()

    def remove_like(self, user):
        """Removes the 'like' relationship between this comment and
        passed user, also updates this comment's 'likes_quantity' attribute.
        """
        if self.likes.filter(pk=user.pk).exists():
            self.likes.remove(user)
            self.likes_quantity -= 1
            self.save()

    def __str__(self):
        """Returns the user username 
        and the post pk.
        """
        return f'{self.user.username} - CID:{self.pk} - PID:{self.post.pk}'
