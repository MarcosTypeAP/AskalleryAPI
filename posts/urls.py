"""Post URLs."""

# Django
from django.urls import include, path

# REST Framework
from rest_framework import routers

# Views
from posts.views import (
    PostViewSet,
    CommentViewSet,
    serve_temporal_image
)


router = routers.SimpleRouter()
router.register("posts", PostViewSet, basename="posts")
router.register("comments", CommentViewSet, basename="comments")

urlpatterns = [

    path("", include(router.urls)),

    # Retrieve post comments url
    #  re_path(
        #  r'^comments/post/(?P<comment_pk>[^/.]+)/$',
        #  CommentViewSet.as_view({'get': 'post'}),
        #  name='comments-post'
    #  )

    path(
        'tmpimage/<str:image>',
        serve_temporal_image,
        name='serve-tmp-image'
    )

]
