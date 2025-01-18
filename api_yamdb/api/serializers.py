from rest_framework import serializers

from reviews.models import Category, Genre, Title, Comment, Review


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.
    Сериализатор преобразует объект категории в формат JSON и обратно.
    """
    class Meta:
        fields = ('name', 'slug')
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Genre.
    Этот сериализатор преобразует объект жанра в формат JSON и обратно.
    """
    class Meta:
        fields = ('name', 'slug')
        model = Genre
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Title (чтение данных).
    Этот сериализатор преобразует объект произведения в формат JSON, включая
    информацию о категории и жанре. Рейтинг возвращается в виде целого числа.
    """
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Title (запись данных).
    Этот сериализатор используется для преобразования данных произведения
    в формат JSON при записи в базу данных.
    """
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    author = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = Review
        fields = (
            'id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        """Запрещает пользователям оставлять повторные отзывы."""
        if not self.context.get('request').method == 'POST':
            return data
        author = self.context.get('request').user
        title_id = self.context.get('view').kwargs.get('title_id')
        if Review.objects.filter(author=author, title=title_id).exists():
            raise serializers.ValidationError(
                'У вас уже есть отзыв на это произведение'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Comment."""

    author = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = Comment
        fields = (
            'id', 'text', 'author', 'pub_date')
