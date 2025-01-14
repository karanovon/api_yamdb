from django.db.models import Avg
from django_filters import rest_framework
from rest_framework import filters, viewsets

from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleWriteSerializer
)
from reviews.models import Category, Genre, Title


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
