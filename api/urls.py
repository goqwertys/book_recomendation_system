from django.urls import path, include
from rest_framework.permissions import AllowAny
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views import UserViewSet, BookViewSet, GenreViewSet, InteractionViewSet, UserRegisterView, AuthorViewSet, \
    get_collaborative_recommendations, get_pagerank_recommendations, get_knn_recommendations, get_statistics

router = SimpleRouter()
router.register('users', UserViewSet)
router.register('books', BookViewSet)
router.register('genres', GenreViewSet)
router.register('authors', AuthorViewSet)
router.register('interactions', InteractionViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # Auth
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(permission_classes=(AllowAny,)), name='refresh'),
    path('users/me/', UserViewSet.as_view({'get': 'me', 'put': 'me', 'patch': 'me'}), name='user-me'),

    # User management
    path('users/<int:pk>/block/', UserViewSet.as_view({'post': 'block'}), name='user-block'),

    # Recommendations for the current user
    path('users/me/pagerank/', get_pagerank_recommendations, name='get-my-pr-recommendations'),
    path('users/me/collaborative/', get_collaborative_recommendations, name='get-my-collaborative-recommendations'),
    path('users/me/knn/', get_knn_recommendations, name='get-my-knn-recommendations'),

    # Recommendations for other users (only for moderators or admins)
    path('recommendations/pagerank/<int:user_id>/', get_pagerank_recommendations, name='get-pr-recommendations'),
    path('recommendations/collaborative/<int:user_id>/', get_collaborative_recommendations, name='get-recommendations'),
    path('recommendations/knn/<int:user_id>/', get_knn_recommendations, name='get-knn-recommendations'),

    # Statistics
    path('statistics/', get_statistics, name='statistics')
]
