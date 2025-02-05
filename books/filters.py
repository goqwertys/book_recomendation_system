import django_filters

from books.models import Book


class BookFilter(django_filters.FilterSet):
    """ Book filter """
    genre = django_filters.CharFilter(field_name='genre__name', lookup_expr='icontains', label='Genre')
    author = django_filters.CharFilter(field_name='author__name', lookup_expr='icontains', label='Author')
    description = django_filters.CharFilter(field_name='description', lookup_expr='icontains', label='description')

    class Meta:
        model = Book
        fields = ['genre', 'author', 'description']
