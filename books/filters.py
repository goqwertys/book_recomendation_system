import django_filters

from books.models import Book, Genre


class BookFilter(django_filters.FilterSet):
    """ Book filter """
    genres = django_filters.ModelChoiceFilter(queryset=Genre.objects.all(), label='Genre')
    author = django_filters.CharFilter(field_name='author__name', lookup_expr='icontains', label='Author')
    description = django_filters.CharFilter(field_name='description', lookup_expr='icontains', label='description')

    class Meta:
        model = Book
        fields = ['genres', 'author', 'description']
