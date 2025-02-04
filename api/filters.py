from django_filters import rest_framework as filters

from books.models import Author, Genre, Book
from users.models import User


class GenreFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Genre
        fields = ['name']


class AuthorFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    bio = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Author
        fields = ['name', 'bio']


class BookFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    author = filters.CharFilter(
        field_name='author__name',
        lookup_expr='icontains'
    )
    author_id = filters.NumberFilter(field_name='author__id')
    genres = filters.ModelChoiceFilter(
        field_name='genres__name',
        queryset=Genre.objects.all(),
        lookup_expr='icontains'
    )
    genre_id = filters.NumberFilter(field_name='genres__id')

    class Meta:
        model = Book
        fields = ['title', 'description', 'author', 'genres']


class UserFilter(filters.FilterSet):
    email = filters.CharFilter(lookup_expr='icontains')
    preferred_genres = filters.ModelChoiceFilter(
        field_name='preferred_genres__name',
        queryset=Genre.objects.all(),
        lookup_expr='icontains'
    )

    class Meta:
        model = User
        fields = ['email', 'preferred_genres']
