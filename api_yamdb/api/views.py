from django.db.models import Avg, QuerySet
from django_filters import rest_framework
from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets, permissions
from rest_framework.serializers import Serializer
from rest_framework.permissions import BasePermission
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    CommentSerializer,
    ReviewSerializer
)
from reviews.models import Category, Genre, Title, Review


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
