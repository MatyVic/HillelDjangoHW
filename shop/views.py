from django.db.models import Q, Avg, Count
from django.shortcuts import render
import shop.models

# Create your views here.

def main(request):

    autor = shop.models.Autor.objects.get(pk=1)
    cheap_books = shop.models.Book.objects.filter(price__lt=5)
    recent_books = shop.models.Book.objects.filter(published_year__gt=1805)
    search_books = shop.models.Book.objects.filter(Q(autor__last_name__incontain='nko') | Q(amount__gt=1))
    avg_price_per_category = shop.models.Category.objects.annotate(avg_price=Avg("book__price"))
    counted_books = shop.models.Book.objects.annotate(book_count=Count("book__price"))


    return ''
