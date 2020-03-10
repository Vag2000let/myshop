import os
import json

from django.core.management.base import BaseCommand

from authapp.models import ShopUser
from mainapp.models import ProductCategory, Product
from django.conf import settings


def load_from_json(file_name):
    with open(os.path.join(settings.JSON_PATH, file_name + '.json'), 'r', encoding='utf-8') as infile:
        return json.load(infile)


class Command(BaseCommand):
    help = 'Fill DB new data'

    def handle(self, *args, **options):
        categories = load_from_json('categories')

        ProductCategory.objects.all().delete()
        [ProductCategory.objects.create(**category) for category in categories]

        products = load_from_json('products')

        Product.objects.all().delete()
        for product in products:
            product['category'] = ProductCategory.objects.get(name=product["category"])
            Product.objects.create(**product)

        # Создаем суперпользователя при помощи менеджера модели
        if not ShopUser.objects.filter(username='django').exists():
                ShopUser.objects.create_superuser('django', 'django@geekshop.local', 'geekbrains', age=25)



