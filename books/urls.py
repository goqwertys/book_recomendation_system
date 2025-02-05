from django.urls import path
from books.apps import BooksConfig
from books.views import HomeView, GenreListView, GenreDetailView, GenreCreateView, GenreUpdateView, AuthorListView, \
    AuthorDetailView, AuthorCreateView, AuthorUpdateView, AuthorDeleteView, BookCreateView, BookDetailView, \
    BookListView, GenreDeleteView, BookUpdateView, BookDeleteView, StatisticsView

app_name = BooksConfig.name

urlpatterns = [
    # Authors CRUD
    path('authors/', AuthorListView.as_view(), name='authors'),
    path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author-detail'),
    path('authors/new/', AuthorCreateView.as_view(), name='author-create'),
    path('authors/<int:pk>/edit/', AuthorUpdateView.as_view(), name='author-update'),
    path('authors/<int:pk>/delete/', AuthorDeleteView.as_view(), name='author-delete'),

    # Genres CRUD
    path('genres/', GenreListView.as_view(), name='genres'),
    path('genres/<int:pk>/', GenreDetailView.as_view(), name='genre-detail'),
    path('genres/new/', GenreCreateView.as_view(), name='genre-create'),
    path('genres/<int:pk>/edit/', GenreUpdateView.as_view(), name='genre-update'),
    path('genres/<int:pk>/delete/', GenreDeleteView.as_view(), name='genre-delete'),

    # Books CRUD
    path('books/', BookListView.as_view(), name='books'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('books/new/', BookCreateView.as_view(), name='book-create'),
    path('books/<int:pk>/edit/', BookUpdateView.as_view(), name='book-update'),
    path('books/<int:pk>/delete/', BookDeleteView.as_view(), name='book-delete'),

    # Home
    path('', HomeView.as_view(), name='home'),

    # Recommendations

    # Statistics
    path('statistics/', StatisticsView.as_view(), name='statistics')
]
