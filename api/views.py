from django.db.models import Avg, Count, Q
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, permissions, mixins, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import AuthorFilter, GenreFilter, BookFilter
from api.paginators import AuthorPaginator, GenrePaginator, BookPaginator, InteractionPaginator, UserPaginator
from api.permissions import IsHimself, IsStaffOrReadOnly, IsOwnerOrStaff
from api.serializers import GenreSerializer, AuthorSerializer, BookSerializer, InteractionSerializer, UserSerializer, \
    UserRegistrationSerializer, UserUpdateSerializer, PageRankRecommendationSerializer, \
    CollaborativeRecommendationSerializer
from books.models import Author, Genre, Book
from config.settings import CACHE_ENABLED
from interactions.models import Interaction
from recommendations.services import get_pagerank_recommendations_service, get_collaborative_recommendations_service, \
    get_knn_recommendations_service
from users.models import User


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    pagination_class = AuthorPaginator
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = AuthorFilter
    ordering_fields = ['name']
    search_fields = ['name', 'bio']
    permission_classes = [IsStaffOrReadOnly]


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = GenrePaginator
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = GenreFilter
    ordering_fields = ['name']
    search_fields = ['name']
    permission_classes = [IsStaffOrReadOnly]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = BookPaginator
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = BookFilter
    ordering_fields = ['average_rating', 'publish_date']
    search_fields = ['name']
    permission_classes = [IsStaffOrReadOnly]


class InteractionViewSet(viewsets.ModelViewSet):
    queryset = Interaction.objects.all()
    serializer_class = InteractionSerializer
    pagination_class = InteractionPaginator
    permission_classes = [IsOwnerOrStaff]

    def perform_create(self, serializer):
        """
        Automatically adds the current user to the `user` field.
        """
        serializer.save(user=self.request.user)


class UserViewSet(viewsets.GenericViewSet,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsHimself]
    pagination_class = UserPaginator

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'update':
            return UserUpdateSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['GET', 'PUT', 'PATCH'])
    def me(self, request):
        user = request.user
        if request.method in ['PUT', 'PATCH']:
            serializer = UserUpdateSerializer(user, data=request.data, partial=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        serializer = self.get_serializer(user)
        return Response(serializer.data)

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['email']
    ordering_fields = ['email']
    search_fields = ['email', 'preferred_genres']


class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pagerank_recommendations(request, user_id):
    data = get_pagerank_recommendations_service(user_id)
    serializer = PageRankRecommendationSerializer(data, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_collaborative_recommendations(request, user_id):
    data = get_collaborative_recommendations_service(user_id)
    serializer = CollaborativeRecommendationSerializer(data, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_knn_recommendations(request, user_id):
    nearest_neighbors = get_knn_recommendations_service(user_id)
    serializer = UserSerializer(nearest_neighbors, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@cache_page(900 if CACHE_ENABLED else 0)
@permission_classes([IsAuthenticated])
def get_statistics(request):
    # Total number of books
    books_count = Book.objects.all().count()

    # Total number of users
    users_count = User.objects.all().count()

    # Number of new books per week
    one_week_ago = timezone.now() - timezone.timedelta(days=7)
    new_books_week_count = Book.objects.filter(publish_date__gte=one_week_ago).count()

    # Top 5 Popular Books with the Highest Average Rating
    top_rated_books = Book.objects.annotate(
        avg_rating=Avg('interaction__rating'),
        rating_count=Count('interaction__rating')
    ).order_by('-avg_rating', '-rating_count')[:5]

    # Top 5 most active users (most interactions per week)
    top_active_users = User.objects.annotate(
        interaction_count=Count(
            'interaction',
            filter=Q(interaction__timestamp__gte=one_week_ago)
        )
    ).order_by('-interaction_count')[:5]

    # Serializing
    top_rated_books_data = BookSerializer(top_rated_books, many=True).data
    top_active_users_data = UserSerializer(top_active_users, many=True).data

    response = {
        'books_count': books_count,
        'users_count': users_count,
        'new_books_week_count': new_books_week_count,
        'top_rated_books': top_rated_books_data,
        'top_active_users': top_active_users_data
    }
    return Response(response)
