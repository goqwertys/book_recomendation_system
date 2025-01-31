from django.contrib import admin

from books.models import Author, Genre, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'bio'
    )
    search_fields = (
        'name',
        'bio',
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )
    search_fields = (
        'name',
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'get_author_name',
        'description',
        'cover',
        'get_genres',
        'publish_date'
    )
    list_filter = (
        'genres',
    )
    search_fields = (
        'title',
        'author__name',
        'genres__name'
    )

    def get_author_name(self, obj):
        """ Returns an author name """
        return obj.author.name if obj.author.name else 'No author'

    get_author_name.short_description = 'Author'

    def get_genres(self, obj):
        """ Returns a string of genres """
        return ', '.join([genre.name for genre in obj.genres.all()])

    get_genres.short_description = 'Genres'
