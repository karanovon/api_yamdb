from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

from . import constants


ROLES = (
    ('admin', 'admin'),
    ('moderator', 'moderator'),
    ('user', 'user'),
)


class User(AbstractUser):
    email = models.EmailField(max_length=constants.EMAIL_LENGHT, unique=True)
    username = models.CharField(max_length=constants.NAME_LENGHT, unique=True)
    first_name = models.CharField(max_length=constants.NAME_LENGHT, blank=True)
    last_name = models.CharField(max_length=constants.NAME_LENGHT, blank=True)
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=constants.ROLE_LENGHT,
        default='user',
        blank=True,
        choices=ROLES
    )

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    class Meta:
        ordering = ('username',)


class Category(models.Model):
    name = models.CharField(max_length=constants.FIELD_LENGTH)
    slug = models.SlugField(unique=True, max_length=constants.SLUG_LENGTH)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=constants.FIELD_LENGTH)
    slug = models.SlugField(unique=True, max_length=constants.SLUG_LENGTH)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=constants.FIELD_LENGTH)
    year = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    genre = models.ManyToManyField(Genre, related_name='titles')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    """Класс отзывов."""

    text = models.TextField(verbose_name='текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Aвтор'
    )
    score = models.PositiveIntegerField(
        verbose_name='Oценка',
        validators=[
            MinValueValidator(1, message='Введенная оценка ниже допустимой'),
            MaxValueValidator(10, message='Введенная оценка выше допустимой'),
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='произведение',
        null=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            ),
        )

    def __str__(self):
        return self.text[:constants.SLUG_LENGTH]


class Comment(models.Model):
    """Класс комментариев."""

    text = models.TextField(verbose_name='текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Aвтор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='oтзыв',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:constants.SLUG_LENGTH]
