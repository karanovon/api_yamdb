from django.db import models
from django.db.models import Manager
from django.core.validators import MaxValueValidator, MinValueValidator

# Константа для ограничения длины текста
LENGTH_TEXT: int = 50


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
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

    text: models.TextField = models.TextField(verbose_name='текст')
    author: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Aвтор'
    )
    score: models.PositiveIntegerField = models.PositiveIntegerField(
        verbose_name='Oценка',
        validators=[
            MinValueValidator(1, message='Введенная оценка ниже допустимой'),
            MaxValueValidator(10, message='Введенная оценка выше допустимой'),
        ]
    )
    pub_date: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )
    title: models.ForeignKey = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='произведение',
        null=True
    )
    comments: Manager["Comment"]  # Связь с Comment

    class Meta:
        verbose_name: str = 'Отзыв'
        verbose_name_plural: str = 'Отзывы'
        ordering: tuple[str] = ('-pub_date',)
        constraints: tuple[models.UniqueConstraint] = (
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            ),
        )

    def __str__(self) -> str:
        return self.text[:LENGTH_TEXT]


class Comment(models.Model):
    """Класс комментариев."""

    text: models.TextField = models.TextField(verbose_name='текст')
    author: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Aвтор'
    )
    pub_date: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )
    review: models.ForeignKey = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='oтзыв',
    )

    class Meta:
        verbose_name: str = 'Комментарий'
        verbose_name_plural: str = 'Комментарии'
        ordering: tuple[str] = ('-pub_date',)

    def __str__(self) -> str:
        return self.text[:LENGTH_TEXT]
