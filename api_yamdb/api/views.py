from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User

from api_yamdb.settings import EMAIL_ADRESS

from .filters import TitleFilter
from .paginations import CommentsSetPagination, ReviewsSetPagination
from .permissions import (AdminModeratorAuthorOrReadOnly, IsAdminOnly,
                          IsAdminOrReadOnly)
from .serializers import (CategorySerializer, CommentsSerializer,
                          GenreSerializer, GetConfirmationCodeSerializer,
                          GetTokenSerializer, ReviewSerializer,
                          TitlesSerializer, UserForAdminSerializer,
                          UserSerializer)


class CreateDestroyListViewSet(mixins.DestroyModelMixin,
                               mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               viewsets.GenericViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CreateDestroyListViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateDestroyListViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitlesSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    queryset = Title.objects.annotate(
        rating=Avg('review_titles__score')
    ).order_by('pk')

    def perform_create(self, serializer):
        tmp = self.request.data.copy()
        slug_category = tmp.pop('category')
        category = get_object_or_404(Category, slug=slug_category[0])
        slug_genres = tmp.pop('genre')
        genres = Genre.objects.filter(slug__in=slug_genres)
        serializer.save(category=category, genre=genres)

    def perform_update(self, serializer):
        instance = serializer.save()
        category = instance.category
        genres = instance.genre.all()
        tmp = self.request.data.copy()
        slug_category = tmp.pop('category', False)
        if slug_category:
            category = get_object_or_404(Category, slug=slug_category[0])
        slug_genres = tmp.pop('genre', False)
        if slug_genres:
            genres = Genre.objects.filter(slug__in=slug_genres)
        serializer.save(category=category, genre=genres)


class ReviewViewSet(viewsets.ModelViewSet):
    """Представление для вывода списка обзоров."""

    serializer_class = ReviewSerializer
    pagination_class = ReviewsSetPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          AdminModeratorAuthorOrReadOnly,
                          )

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title.review_titles.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentsViewSet(viewsets.ModelViewSet):
    """Представление для вывода списка обзоров."""

    serializer_class = CommentsSerializer
    pagination_class = CommentsSetPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          AdminModeratorAuthorOrReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, title=title_id, pk=review_id)
        return review.comment.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, title=title_id, pk=review_id)
        serializer.save(author=self.request.user, review_id=review)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserForAdminSerializer
    permission_classes = (IsAdminOnly,)
    lookup_field = 'username'
    search_fields = ('=username',)
    pagination_class = PageNumberPagination

    @action(detail=False, methods=['GET', 'PATCH'],
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        if request.method != 'PATCH':
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(
            request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserNameViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = None
    filterset_fields = ('username')


class GetConfirmationCodeView(APIView):
    http_method_names = ['post', ]
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = GetConfirmationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        if User.objects.filter(username=username).exists():
            message = 'Пользователь с таким username уже существует'
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            message = 'Пользователь с таким email уже существует'
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create(username=username, email=email)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Вы зарегистрировались на ресурсе API.',
            f'Вот ваш код-подтверждение: {confirmation_code}',
            EMAIL_ADRESS,
            (email,),
            fail_silently=False,
        )
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class GetTokenApiView(APIView):
    http_method_names = ['post', ]
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        confirmation_code = serializer.validated_data.get('confirmation_code')
        if default_token_generator.check_token(user, confirmation_code):
            access_token = RefreshToken.for_user(user).access_token
            data = {'token': str(access_token)}
            return Response(data, status=status.HTTP_201_CREATED)
        errors = {'error': 'confirmation code is incorrect'}
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
