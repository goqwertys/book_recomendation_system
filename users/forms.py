from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms

from books.models import Genre
from users.models import User


class UserRegisterForm(UserCreationForm):
    preferred_genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'avatar', 'preferred_genres']
        labels = {
            'email': 'Email',
            'avatar': 'Avatar'
        }


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
