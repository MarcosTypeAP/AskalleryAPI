"""Posts Admin."""

# Django
from django.contrib import admin

# Models
from posts.models import Post, Comment


admin.site.register(Post)
admin.site.register(Comment)