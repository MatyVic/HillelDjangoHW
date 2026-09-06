from django.db.models import Avg
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Book, Rating


@receiver([post_save, post_delete], sender=Book)
def invalidate_book_detail_cache(sender, instance, **kwargs):
    cache.delete(f"book:detail:{instance.pk}")


@receiver(post_save, sender=Rating)
def update_rating(sender, instance, created, **kwargs):
    if created:
        rated_book = instance.book
        rated_book.calculated_rating = rated_book.rating_set.aggregate(Avg('rating'))['rating__avg']
        rated_book.save()