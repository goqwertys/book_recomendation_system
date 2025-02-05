from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, DeleteView, CreateView, UpdateView, DetailView

from books.filters import BookFilter
from books.forms import GenreForm, AuthorForm, BookForm
from books.models import Genre, Author, Book
from interactions.forms import RatingForm
from interactions.models import Interaction
from recommendations.services import get_statistics, get_collaborative_recommendations_service, \
    get_knn_recommendations_service, get_pagerank_recommendations_service


class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to check if a user is a moderator (is_staff)."""
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        raise PermissionDenied("You do not have permission to perform this action.")


class HomeView(TemplateView):
    """ Home view"""
    template_name = 'books/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# Genre CRUD
class GenreListView(StaffRequiredMixin, ListView):
    model = Genre
    template_mame = 'books/genre_list.html'
    context_object_name = 'genres'
    paginate_by = 10


class GenreDetailView(StaffRequiredMixin, DetailView):
    model = Genre
    template_name = 'books/genre_detail.html'
    context_object_name = 'genre'


class GenreCreateView(StaffRequiredMixin, CreateView):
    model = Genre
    form_class = GenreForm
    template_name = 'books/genre_form.html'
    success_url = reverse_lazy('books:genres')


class GenreUpdateView(StaffRequiredMixin, UpdateView):
    model = Genre
    form_class = GenreForm
    template_name = 'books/genre_form.html'
    success_url = reverse_lazy('books:genres')


class GenreDeleteView(StaffRequiredMixin, DeleteView):
    model = Genre
    template_name = 'books/genre_confirm_delete.html'
    success_url = reverse_lazy('books:genres')


# Author CRUD
class AuthorListView(StaffRequiredMixin, ListView):
    model = Author
    template_name = 'books/author_list.html'
    context_object_name = 'authors'
    paginate_by = 10


class AuthorDetailView(StaffRequiredMixin, DetailView):
    model = Author
    template_name = 'books/author_detail.html'
    context_object_name = 'author'


class AuthorCreateView(StaffRequiredMixin, CreateView):
    model = Author
    form_class = AuthorForm
    template_name = 'books/author_form.html'
    success_url = reverse_lazy('books:authors')


class AuthorUpdateView(StaffRequiredMixin, UpdateView):
    model = Author
    form_class = AuthorForm
    template_name = 'books/author_form.html'
    success_url = reverse_lazy('books:authors')


class AuthorDeleteView(StaffRequiredMixin, DeleteView):
    model = Author
    template_name = 'books/author_confirm_delete.html'
    success_url = reverse_lazy('books:authors')


# Book CRUD
class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 10
    filterset_class = BookFilter

    def get_queryset(self):
        """ Searching, filtering, and sorting """
        queryset = super().get_queryset()

        search_query = self.request.GET.get('q', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        genre_filter = self.request.GET.get('genres', '')
        if genre_filter:
            queryset = queryset.filter(genres__id=genre_filter)

        ordering = self.request.GET.get('sort', '-publish_date')
        allowed_sort_fields = ['title', '-title', 'publish_date', '-publish_date', 'rating', '-rating']
        if ordering in allowed_sort_fields:
            queryset = queryset.order_by(ordering)

        return queryset

    def get_context_data(self, **kwargs):
        """ Add filters to context """
        context = super().get_context_data(**kwargs)
        context['filter'] = BookFilter(self.request.GET, queryset=self.get_queryset())
        return context


@method_decorator(login_required, name='dispatch')
class BookDetailView(DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        interaction = Interaction.objects.filter(user=self.request.user, book=book).first()
        context['rating_form'] = RatingForm(instance=interaction)
        context['user_rating'] = interaction.rating if interaction else None
        return context

    def post(self, request, *args, **kwargs):
        book = self.get_object()
        interaction, created = Interaction.objects.get_or_create(user=request.user, book=book)
        form = RatingForm(request.POST, instance=interaction)
        if form.is_valid():
            form.save()
        return redirect('books:book-detail', pk=book.pk)


class BookCreateView(StaffRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('books:books')


class BookUpdateView(StaffRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('books:books')


class BookDeleteView(StaffRequiredMixin, DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('books:books')


class StatisticsView(TemplateView):
    """ Home view"""
    template_name = 'books/statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        statistics_data = get_statistics()
        context['books_count'] = statistics_data['books_count']
        context['users_count'] = statistics_data['users_count']
        context['new_books_week_count'] = statistics_data['new_books_week_count']
        context['top_rated_books'] = statistics_data['top_rated_books']
        context['top_active_users'] = statistics_data['top_active_users']

        return context


class RecommendationView(LoginRequiredMixin, TemplateView):
    """ Recommendation view """
    template_name = 'books/recommendations.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        context["pagerank_recommendations"] = get_pagerank_recommendations_service(user_id)
        context['collaborative_recommendations'] = get_collaborative_recommendations_service(user_id)
        context['knn_recommendations'] = get_knn_recommendations_service(user_id)

        return context
