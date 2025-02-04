from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms

import books
from books.forms import StyleFormMixin
from books.models import Genre
from users.models import User


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    avatar = forms.ImageField(required=False, label='Avatar')
    preferred_genres = forms.ModelMultipleChoiceField(
        queryset=books.models.Genre.objects.all(),
        required=False,
        label='Preferred Genres'
    )
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'avatar', 'preferred_genres')


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')


class UserUpdateForm(forms.ModelForm):
    preferred_genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = User
        fields = ['email', 'avatar', 'preferred_genres']
