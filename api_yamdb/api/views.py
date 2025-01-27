from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg, QuerySet
from django_filters import rest_framework
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.views import APIView


from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    CommentSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TokenSerializer,
    UserSerializer,
    EditUserSerializer
)
from reviews.models import Category, Genre, Title, Review, User

from .filters import TitleFilter
from .permissions import (
    IsAdminOrReadOnly,
    IsAdminOrSuperUser,
    IsAuthorOrReadOnly, IsStaffOrAuthorOrReadOnly
)


class SignupUser(APIView):
    """Отправка кода подтверждения на почту."""

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, _ = User.objects.get_or_create(**serializer.validated_data)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Confirmation code from YamDB',
            message=f'code_confirmation {confirmation_code}',
            from_email='api_yamdb@mail.ru',
            recipient_list=[user.email],
        )
        return Response(
            {
                'username': user.username,
                'email': user.email
            },
            status=status.HTTP_200_OK
        )


class Token(APIView):
    """Выдача токена после отправки кода подтверждения."""

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


class UserViewSet(viewsets.ModelViewSet):
    """Управление пользователями админом и суперпользователем."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)
    permission_classes = (IsAdminOrSuperUser, IsAuthorOrReadOnly)
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete',)

    """Ресурс для управлением собственным профилем
    авторизованного пользователя."""
    @action(
        methods=('get', 'patch',),
        detail=False,
        url_path='me',
        permission_classes=[permissions.IsAuthenticated],)
    def me(self, request):
        user = request.user
        if request.method == "GET":
            serializer = UserSerializer(
                user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
        serializer = EditUserSerializer(
            user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с категориями."""
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'delete']

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с жанрами."""
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'delete']

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TitleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с произведениями.
    В процессе получения данных для произведений
    вычисляется рейтинг на основе оценок в отзывах.
    """
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('-rating')
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = TitleFilter
    filter_backends = (rest_framework.DjangoFilterBackend, SearchFilter)
    search_fields = ('name',)
    http_method_names = ['get', 'post', 'delete', 'patch']

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
        IsStaffOrAuthorOrReadOnly
    )
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']

    def get_title(self) -> Title:
        """
        Возвращает объект текущего произведения.

        Raises:
            NotFound: Если title_id отсутствует в параметрах запроса.
        """
        title_id = self.kwargs.get('title_id')
        if not title_id:
            raise NotFound('title_id отсутствует в параметрах запроса.')
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self) -> QuerySet[Review]:
        """Возвращает queryset с отзывами для текущего произведения."""
        title = self.get_title()
        return title.reviews.select_related('author')

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
        IsStaffOrAuthorOrReadOnly,
    )
    http_method_names = ['get', 'post', 'patch', 'delete']

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
