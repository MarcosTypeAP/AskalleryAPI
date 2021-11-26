"""Post URLs."""

# Django
from django.urls import include, path, re_path

# REST Framework
from rest_framework import routers

# Views
from posts import views as post_views


router = routers.SimpleRouter()
router.register("posts", post_views.PostViewSet, basename="posts")

urlpatterns = [

    path("", include(router.urls)),

    # delete comment url
    re_path(
        r'^posts/(?P<post_pk>[^/.]+)/comment/(?P<comment_pk>[^/.]+)/$',
        post_views.PostViewSet.as_view({'delete': 'comment'}),
        name='posts-comment'
    )

]

for url in router.urls:
    print(url)

print('\n')

for url in urlpatterns:
    print(url)
