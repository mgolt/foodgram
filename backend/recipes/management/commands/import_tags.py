import csv

from django.core.management.base import BaseCommand

from foodgram.settings import CSV_FILE_DIR
from recipes.models import Tags


class Command(BaseCommand):    

    def handle(self, *args, **kwargs):
        with open(
                f'{CSV_FILE_DIR}/tags.csv', encoding='utf-8'
        ) as file:
            reader = csv.reader(file)
            next(reader)
            tags = [
                Tags(
                    name=row[0],
                    slug=row[1],
                )
                for row in reader
            ]
            Tags.objects.bulk_create(tags)

        print('Теги импортированы!')
