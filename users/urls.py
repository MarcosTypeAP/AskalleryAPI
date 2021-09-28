"""User URLs."""

# Django
from django.urls import include, path

# REST Framework
from rest_framework.routers import SimpleRouter

# Views
from users import views as user_views

# Simple JWT
from rest_framework_simplejwt import views as token_views 


router = SimpleRouter()
router.register('users', user_views.UserViewSet, basename='users')

urlpatterns = [

    path('', include(router.urls)),

    # Simple JWT
    path('token/', token_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', token_views.TokenRefreshView.as_view(), name='token_refresh'),

]
