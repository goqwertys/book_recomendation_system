from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, permissions, mixins, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import AuthorFilter, GenreFilter, BookFilter
from api.paginators import AuthorPaginator, GenrePaginator, BookPaginator, InteractionPaginator, UserPaginator
from api.permissions import IsHimself, IsStaffOrReadOnly, IsOwnerOrStaff, IsAdminUser
from api.serializers import GenreSerializer, AuthorSerializer, BookSerializer, InteractionSerializer, UserSerializer, \
    UserRegistrationSerializer, UserUpdateSerializer, PageRankRecommendationSerializer, \
    CollaborativeRecommendationSerializer
from books.models import Author, Genre, Book
from interactions.models import Interaction
from recommendations.services import get_pagerank_recommendations_service, get_collaborative_recommendations_service, \
    get_knn_recommendations_service, get_statistics
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

    def get_queryset(self):
        """
        Limit requests:
        - Users can only see their own interactions.
        - Moderators can see all interactions.
        """
        user = self.request.user
        if user.is_staff:
            return Interaction.objects.all()
        return Interaction.objects.filter(user=user)

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

    @action(detail=False, methods=['GET', 'PUT', 'PATCH'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """ Getting and editing the current user's profile """
        user = request.user

        if request.method in ['PUT', 'PATCH']:
            serializer = UserUpdateSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'], permission_classes=[IsAdminUser])
    def block(self, request, pk=None):
        """
        Blocks/ Unblocks the user, switching `is_active`.
        Only available to moderators (`is_staff`).
        """
        try:
            user = self.get_object()

            if user == request.user:
                return Response({'detail': 'You cannot block yourself.'}, status=403)

            user.is_active = not user.is_active
            user.save()

            status = "Blocked" if not user.is_active else "Unblocked"
            return Response({'detail': f'User {user.pk} is now {status}.'})

        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=404)

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['email']
    ordering_fields = ['email']
    search_fields = ['email', 'preferred_genres']


class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pagerank_recommendations(request, user_id=None):
    if user_id is None:
        user = request.user
    else:
        if not request.user.is_staff:
            return Response(
                {
                    'detail':'You do not have permission to view recommendations for other users.'
                },
                status=403
            )
        user = User.objects.get(id=user_id)

    data = get_pagerank_recommendations_service(user.id)
    serializer = PageRankRecommendationSerializer(data, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_collaborative_recommendations(request, user_id):
    if user_id is None:
        user = request.user
    else:
        if not request.user.is_staff:
            return Response(
                {
                    'detail': 'You do not have permission to view recommendations for other users.'
                },
                status=403
            )
        user = User.objects.get(id=user_id)

    data = get_collaborative_recommendations_service(user.id)
    serializer = CollaborativeRecommendationSerializer(data, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_knn_recommendations(request, user_id):
    if user_id is None:
        user = request.user
    else:
        if not request.user.is_staff:
            return Response(
                {
                    'detail': 'You do not have permission to view recommendations for other users.'
                },
                status=403
            )
        user = User.objects.get(id=user_id)

    nearest_neighbors = get_knn_recommendations_service(user.id)
    serializer = UserSerializer(nearest_neighbors, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_statistics_api(request):
    statistics_data = get_statistics()

    # Serializing data
    top_rated_books_data = BookSerializer(statistics_data['top_rated_books'], many=True).data
    top_active_users_data = UserSerializer(statistics_data['top_active_users'], many=True).data

    response = {
        'books_count': statistics_data['books_count'],
        'users_count': statistics_data['users_count'],
        'new_books_week_count': statistics_data['new_books_week_count'],
        'top_rated_books': top_rated_books_data,
        'top_active_users': top_active_users_data
    }
    return Response(response)
