"""Askallery model utils."""

# Django
from django.db import models


class AskalleryModel(models.Model):
    """Askallery base model.
    
    AskalleryModel acts as an abstract base class which
    will be inherited by all other models in the project.
    This class provides every table with some Meta class settings
    and the following attributes:

    + created (DateTime): Stores the datetime when the object was created.

    + modified (DateTime): Stores the datetime when the object was last modified.
    """

    created = models.DateTimeField(
        'created at',
        auto_now_add=True,
        help_text='Stores the datetime when the object was created.'
    )

    modified = models.DateTimeField(
        'modified at',
        auto_now=True,
        help_text='Stores the datetime when the object was last modified'
    )

    class Meta:
        """Meta options."""
        abstract = True

        get_latest_by = 'created'
        ordering = ('-created', '-modified')