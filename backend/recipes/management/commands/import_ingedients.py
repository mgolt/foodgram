import csv

from django.core.management.base import BaseCommand

from foodgram.settings import CSV_FILE_DIR
from recipes.models import Ingredients


class Command(BaseCommand):    

    def handle(self, *args, **kwargs):
        with open(
                f'{CSV_FILE_DIR}/ingredients.csv', encoding='utf-8'
        ) as file:
            reader = csv.reader(file)
            next(reader)
            ingredients = [
                Ingredients(
                    name=row[0],
                    measurement_unit=row[1],
                )
                for row in reader
            ]
            Ingredients.objects.bulk_create(ingredients)

        print('Ингредиенты импортированы!')
