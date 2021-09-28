"""Post URLs."""

# Django
from django.urls import include, path

# REST Framework
from rest_framework import routers

# Views
from posts import views as post_views


router = routers.SimpleRouter()
router.register('posts', post_views.PostViewSet, basename='posts')

urlpatterns = [
    
] 

urlpatterns += router.urls

for url in router.urls:
    print(url, '\n')