from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from reviews.models import Category, Comments, Genre, Review, Title
from users.models import User
from users.validators import validate_user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitlesSerializer(serializers.ModelSerializer):

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField(default=None)

    class Meta:
        model = Title
        fields = ('id',
                  'name',
                  'year',
                  'rating',
                  'description',
                  'genre',
                  'category',)

        validators = [
            UniqueTogetherValidator(
                queryset=Title.objects.all(),
                fields=('name', 'year')
            )
        ]

    def get_rating(self, obj):
        if self.context['view'].request.method == 'POST':
            return None
        if obj.rating is None:
            return obj.rating
        return round(obj.rating, 0)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    def validate(self, data):
        title_id = self.context['view'].kwargs['title_id']
        title = get_object_or_404(Title, pk=title_id)
        if (self.context['view'].request.method == 'POST'
                and title.review_titles.filter(
                    author=self.context['request'].user).exists()):
            raise serializers.ValidationError(
                'Нельзя добавить второй отзыв на одно произведение.')
        return data

    class Meta:
        model = Review

        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        read_only_fields = ('author',)
        validators = []


class CommentsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username')

    class Meta:
        model = Comments
        fields = ('id', 'text', 'author', 'pub_date',)

    def get_author(self, obj):
        return obj.author.username


class UserForAdminSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'email', 'role')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'email', 'role')
        read_only_fields = ('role', 'email')


class GetConfirmationCodeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150, validators=[validate_user])
    email = serializers.EmailField(max_length=254,)

    class Meta:
        model = User
        fields = ['username', 'email']

    def create(self, validated_data):
        user, created = User.objects.get_or_create(**validated_data)
        return user


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()
