"""Post URLs."""

# Django
from django.urls import include, path, re_path

# REST Framework
from rest_framework import routers

# Views
from posts.views import (
    PostViewSet,
    CommentViewSet
)


router = routers.SimpleRouter()
router.register("posts", PostViewSet, basename="posts")
router.register("comments", CommentViewSet, basename="comments")

urlpatterns = [

    path("", include(router.urls)),

    # delete comment url
    #  re_path(
        #  r'^posts/comment/(?P<comment_pk>[^/.]+)/$',
        #  post_views.PostViewSet.as_view({'delete': 'comment'}),
        #  name='posts-comment'
    #  )

]

for url in router.urls:
    print(url)

print('\n')

for url in urlpatterns:
    print(url)
