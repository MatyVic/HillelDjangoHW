from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from shop.models import Rating


@receiver(post_save, sender=Rating)
def update_rating(sender,instance, created, *kwargs):
    if created:
        rated_book = instance.book
        rated_book.calculated_rating = rated_book.ratings.all().aggregate(Sum('rating'))['rating__avg']
        rated_book.save()