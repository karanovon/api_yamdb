import csv

from django.core.management import BaseCommand
from django.conf import settings

from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title,
    User
)

DATA_PATH = f'{settings.BASE_DIR}/static/data'


class Command(BaseCommand):
    """Класс для выгрузки данных из CSV файлов в БД."""

    def handle(self, *args, **kwargs):
        data_files = {
            'categories': ('category.csv', Category),
            'comments': ('comments.csv', Comment),
            'genres': ('genre.csv', Genre),
            'reviews': ('review.csv', Review),
            'titles': ('titles.csv', Title),
            'users': ('users.csv', User)
        }

        for key, (file_path, model) in data_files.items():
            self.stdout.write(f'Очистка данных для модели {key}...')
            model.objects.all().delete()

            self.stdout.write(f'Загрузка данных для модели {key}...')
            self.load_data(file_path, model, key)

        self.stdout.write(self.style.SUCCESS('Все данные успешно загружены'))

    def load_data(self, file_path, model, key):
        """Загружает данные из файла в указанную модель."""
        with open(f'{DATA_PATH}/{file_path}', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            instances = []

            for row in reader:
                row = self.process_row(row, key)
                if row:
                    instances.append(model(**row))

            model.objects.bulk_create(instances)
            self.stdout.write(self.style.SUCCESS(f'Данные {key} загружены'))

    def process_row(self, row, key):
        """Обрабатывает одну строку данных для модели."""
        if key == 'titles':
            return self.process_titles_row(row)
        if key == 'comments':
            return self.process_comments_row(row)
        if key == 'reviews':
            return self.process_reviews_row(row)
        return row

    def process_titles_row(self, row):
        """Обрабатывает строку для модели Title."""
        category_id = row.pop('category')
        try:
            category = Category.objects.get(id=category_id)
            row['category'] = category
            return row
        except Category.DoesNotExist:
            self.stderr.write(
                f"Категория с id={category_id} не найдена. Пропуск строки."
            )
            return None

    def process_comments_row(self, row):
        """Обрабатывает строку для модели Comment."""
        user_id = row.pop('author')
        try:
            user = User.objects.get(id=user_id)
            row['author'] = user
            return row
        except User.DoesNotExist:
            self.stderr.write(
                f"Пользователь с id={user_id} не найден. Пропуск строки."
            )
            return None

    def process_reviews_row(self, row):
        """Обрабатывает строку для модели Review."""
        user_id = row.pop('author')
        try:
            user = User.objects.get(id=user_id)
            row['author'] = user
            return row
        except User.DoesNotExist:
            self.stderr.write(
                f"Пользователь с id={user_id} не найден. Пропуск строки."
            )
            return None
