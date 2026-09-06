from django.apps import AppConfig
from django.db.models.signals import post_save

from shop.models import Rating
from shop.signals import update_rating


class ShopConfig(AppConfig):
    name = 'shop'

    def ready(self):
        post_save.connect(update_rating, sender= Rating)
