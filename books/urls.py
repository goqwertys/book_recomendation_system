from django.urls import path
from books.apps import BooksConfig
from books.views import HomeView

app_name = BooksConfig.name

urlpatterns = [
    # Authors CRUD
    # Genres CRUD
    # Books CRUD
    # Interactions CRUD
    # Home
    path('', HomeView.as_view(), name='home')
]
