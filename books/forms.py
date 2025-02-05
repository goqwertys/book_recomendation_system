from django import forms

from books.models import Genre, Author, Book


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class GenreForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name', ]


class AuthorForm(StyleFormMixin, forms.ModelForm):
    bio = forms.CharField(required=False)

    class Meta:
        model = Author
        fields = ['name', 'bio']


class BookForm(StyleFormMixin, forms.ModelForm):
    cover = forms.ImageField(required=False, label='Cover')
    author = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        label='Author'
    )
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Genres'
    )

    class Meta:
        model = Book
        fields = ['title', 'cover', 'author', 'description', 'genres']
