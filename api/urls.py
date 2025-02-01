from django.urls import path, include
from rest_framework.permissions import AllowAny
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views import UserViewSet, BookViewSet, GenreViewSet, InteractionViewSet, UserRegisterView, AuthorViewSet

router = SimpleRouter()
router.register('users', UserViewSet)
router.register('books', BookViewSet)
router.register('genres', GenreViewSet)
router.register('authors', AuthorViewSet)
router.register('interactions', InteractionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(permission_classes=(AllowAny,)), name='refresh'),
    path('users/me/', UserViewSet.as_view({'get': 'me', 'put': 'me', 'patch': 'me'}), name='user-me')
]
