"""User Admin."""

# Django
from django.contrib import admin

# Models
from users.models import User
from users.models import Profile


admin.site.register(User)
admin.site.register(Profile)
