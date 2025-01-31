from rest_framework import serializers
from books.models import Genre, Author, Book
from users.models import User
from interactions.models import Interaction


class GenreSerializer(serializers.ModelSerializer):
    """ Genre serializer """
    class Meta:
        model = Genre
        fields = ['id', 'name']


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
    preferred_genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'avatar', 'preferred_genres']
        extra_kwargs = {
            'preferred_genres': {'read_only': True}
        }


class InteractionSerializer(serializers.ModelSerializer):
    """ Interaction Serializer """
    class Meta:
        model = Interaction
        fields = '__all__'


class UserRegistrationSerializer(serializers.ModelSerializer):
    """ Serializer for registration """
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'avatar')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """ Serializer for editing profile """
    class Meta:
        model = User
        fields = ['email', 'avatar', 'preferred_genres']
        extra_kwargs = {
            'email': {'required': False},
            'password': {'required': False},
        }

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError('')
        return value
