from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from .permissions import IsAdminOrReadOnly


class BaseCategoryGenreViewSet(viewsets.ModelViewSet):
    """Базовый ViewSet для категорий и жанров."""
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'delete']

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
