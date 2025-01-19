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
            with open(f'{DATA_PATH}/{file_path}', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                instances = []

                for row in reader:
                    if key == 'titles':
                        category_id = row.pop('category')
                        try:
                            category = Category.objects.get(id=category_id)
                            row['category'] = category
                        except Category.DoesNotExist:
                            self.stderr.write(
                                f"Категория с id={category_id} не найдена. "
                                "Пропуск строки."
                            )
                            continue

                    instances.append(model(**row))

                model.objects.bulk_create(instances)
                self.stdout.write(
                    self.style.SUCCESS(f'Данные {key} загружены')
                )

        self.stdout.write(self.style.SUCCESS('Все данные успешно загружены'))
