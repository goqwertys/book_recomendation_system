from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter

from api.views import UserViewSet, BookViewSet, GenreViewSet, InteractionViewSet

router = SimpleRouter()
router.register('users', UserViewSet)
router.register('books', BookViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'interactions', InteractionViewSet)

urlpatterns = [
    path('', include(router.urls))
]
