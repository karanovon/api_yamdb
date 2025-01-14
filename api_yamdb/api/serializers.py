from rest_framework import serializers

from reviews.models import Category, Genre, Title


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
