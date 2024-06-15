import yaml
from django.core.management.base import BaseCommand
from products.models import Product, Supplier

class Command(BaseCommand):
    help = 'Import products from yaml file'

    def handle(self, *args, **kwargs):
        with open('products.yaml', 'r') as file:
            data = yaml.safe_load(file)
            for item in data['products']:
                supplier, _ = Supplier.objects.get_or_create(
                    name=item['supplier']['name'],
                    contact_email=item['supplier']['contact_email']
                )
                Product.objects.create(
                    name=item['name'],
                    description=item['description'],
                    price=item['price'],
                    stock=item['stock'],
                    supplier=supplier
                )