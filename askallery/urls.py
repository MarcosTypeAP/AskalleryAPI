"""Main URLs module."""

# Django
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Django Admin
    path('admin/', admin.site.urls),

    # Users
    path('api/', include(('users.urls', 'users'), namespace='users')),

    # Posts
    path('api/', include(('posts.urls', 'posts'), namespace='posts')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
