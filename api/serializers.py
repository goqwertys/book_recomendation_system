from rest_framework import serializers
from books.models import Genre, Author, Book
from users.models import User
from interactions.models import Interaction


class GenreSerializer(serializers.ModelSerializer):
    """ Genre serializer """
    class Meta:
        model = Genre
        fields = '__all__'


class AuthorSerializer(serializers.ModelSerializer):
    """ Author serializer """
    class Meta:
        model = Author
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    """ Book serializer """
    class Meta:
        model = Book
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """ User serializer """
    class Meta:
        model = User
        fields = ['id', 'email', 'avatar', 'preferred_genres']


class InteractionSerializer(serializers.ModelSerializer):
    """ Interaction Serializer """
    class Meta:
        model = Interaction
        fields = '__all__'
