from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DeleteView, CreateView, UpdateView

from books.forms import GenreForm, AuthorForm, BookForm
from books.models import Genre, Author, Book


class HomeView(TemplateView):
    """ Home view"""
    template_name = 'books/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# Genre CRUD
class GenreListView(ListView, LoginRequiredMixin):
    model = Genre
    template_mame = 'books/genre_list.html'
    context_object_name = 'genres'
    paginate_by = 10


class GenreDetailView(DeleteView, LoginRequiredMixin):
    model = Genre
    template_name = 'books/genre_detail.html'
    context_object_name = 'genre'


class GenreCreateView(CreateView):
    model = Genre
    form_class = GenreForm
    template_name = 'books/genre_form.html'
    success_url = reverse_lazy('books:genres')


class GenreUpdateView(UpdateView):
    model = Genre
    form_class = GenreForm
    template_name = 'books/genre_form.html'
    success_url = reverse_lazy('books:genres')


class GenreDeleteView(DeleteView):
    model = Genre
    template_name = 'books/genre_confirm_delete.html'
    success_url = reverse_lazy('books:genres')


# Author CRUD
class AuthorListView(ListView):
    model = Author
    template_name = 'books/author_list.html'
    context_object_name = 'authors'
    paginate_by = 10


class AuthorDetailView(DeleteView):
    model = Author
    template_name = 'books/author_detail.html'
    context_object_name = 'author'


class AuthorCreateView(CreateView):
    model = Author
    form_class = AuthorForm
    template_name = 'books/author_form.html'
    success_url = reverse_lazy('books:authors')


class AuthorUpdateView(UpdateView):
    model = Author
    form_class = AuthorForm
    template_name = 'books/author_form.html'
    success_url = reverse_lazy('books:authors')


class AuthorDeleteView(DeleteView):
    model = Author
    template_name = 'books/author_confirm_delete.html'
    success_url = reverse_lazy('books:authors')


# Book CRUD
class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 10


class BookDetailView(DeleteView):
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'


class BookCreateView(CreateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('books:books')


class BookUpdateView(UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('books:books')


class BookDeleteView(DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('books:books')
