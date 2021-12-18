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

    likes = models.ManyToManyField('users.User', related_name='post_likes')

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
            'Quantity of ´Comment´ instances related with this post.'
            'Stores the value to perform less queries.'
            'Increase 1 when another user leaves a comment on this post.',
        )
    )

    is_active = models.BooleanField(
        'active',
        default=True,
        help_text='It will be False when the post is removed.'
    )

    def add_like(self, user):
        """Establishes a 'like' relationship between this post and
        passed user, also updates this post's 'likes_quantity' attribute.
        """
        if not self.likes.filter(pk=user.pk).exists():
            self.likes.add(user)
            self.likes_quantity += 1
            self.save()

    def remove_like(self, user):
        """Removes the 'like' relationship between this post and
        passed user, also updates this post's 'likes_quantity' attribute.
        """
        if self.likes.filter(pk=user.pk).exists():
            self.likes.remove(user)
            self.likes_quantity -= 1
            self.save()

    def add_comment(self, user, content):
        """Creates a 'Comment' instance with passed user and content,
        and establishes a relationship between the comment and this post.
        """
        comment = self.comment_set.create(user=user, content=content)
        self.comments_quantity += 1
        self.save()
        return comment

    def remove_comment(self, comment):
        """Removes the given comment instance and also updates
        this comment's 'likes_quantity' attribute.
        """
        self.comment_set.filter(pk=comment).delete()
        self.comments_quantity -= 1
        self.save()

    def __str__(self):
        """Returns the user username and
        a short version of the caption.
        """
        return f'{self.user.username} - {self.caption[:10]}...'
