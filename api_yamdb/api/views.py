from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg, QuerySet
from django_filters import rest_framework
from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.tokens import AccessToken
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    CommentSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TokenSerializer
)
from reviews.models import Category, Genre, Title, Review, User


class SignupUser(APIView):

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, _ = User.objects.get_or_create(**serializer.validated_data)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Confirmation code from yambdb',
            message=(f'code_confirmation {confirmation_code}'),
            from_email='api_yamdb@mail.ru',
            recipient_list=[user.email],
        )
        return Response(
            {'message': 'код подтверждения отправлен на вашу почту'},
            status=status.HTTP_200_OK
        )


class Token(APIView):

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        user = get_object_or_404(User, username=username)
        confirmation_code = serializer.validated_data['confirmation_code']
        if default_token_generator.check_token(user, confirmation_code):
            return Response(
                {'Token': str(AccessToken.for_user(user))},
                status=status.HTTP_200_OK
            )
        return Response(
            {'message': 'Неверный код подтверждения '},
            status=status.HTTP_400_BAD_REQUEST
        )


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с категориями."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с жанрами."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с произведениями.
    В процессе получения данных для произведений
    вычисляется рейтинг на основе оценок в отзывах.
    """
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('-rating')
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (rest_framework.DjangoFilterBackend,)
    search_fields = ('name', 'category__slug', 'genre__slug',)

    def get_serializer_class(self):
        """
        Возвращает сериализатор в зависимости от действия:
        - list и retrieve используют TitleReadSerializer для чтения данных.
        - остальные действия используют TitleWriteSerializer.
        """
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для объектов модели Review."""

    serializer_class: type[Serializer] = ReviewSerializer
    permission_classes: tuple[type[BasePermission], ...] = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_title(self) -> Title:
        """
        Возвращает объект текущего произведения.

        Raises:
            ValueError: Если title_id отсутствует в параметрах запроса.
        """
        title_id = self.kwargs.get('title_id')
        if not title_id:
            raise ValueError('title_id отсутствует в параметрах запроса.')
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self) -> QuerySet[Review]:
        """Возвращает queryset с отзывами для текущего произведения."""
        return self.get_title().reviews.select_related('author').all()  # type: ignore

    def perform_create(self, serializer: Serializer) -> None:
        """
        Создает отзыв для текущего произведения,
        где автором является текущий пользователь.
        """
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для объектов модели Comment."""

    serializer_class: type[Serializer] = CommentSerializer
    permission_classes: tuple[type[BasePermission], ...] = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_review(self) -> Review:
        """
        Возвращает объект текущего отзыва.

        Raises:
            ValueError: Если review_id отсутствует в параметрах запроса.
        """
        review_id = self.kwargs.get('review_id')
        if not review_id:
            raise ValueError('review_id отсутствует в параметрах запроса.')
        return get_object_or_404(Review, pk=review_id)

    def get_queryset(self) -> QuerySet:
        """Возвращает queryset с комментариями для текущего отзыва."""
        return self.get_review().comments.select_related('author').all()

    def perform_create(self, serializer: Serializer) -> None:
        """
        Создает комментарий для текущего отзыва,
        где автором является текущий пользователь.
        """
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )
