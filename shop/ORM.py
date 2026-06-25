from django.db.models import Q, Avg, Count
import shop.models

def get_cheap_books(price = 0):
    cheap_books = shop.models.Book.objects.filter(price__lt=price)

    return cheap_books


def search_books(search_text , amount):
    search_books_res = shop.models.Book.objects.filter(Q(autor__last_name__incontain=search_text) | Q(amount__gt=amount))

    return search_books_res

def get_avg_price_per_category():
    avg_price_per_category = shop.models.Category.objects.annotate(avg_price=Avg("book__price"))

    return avg_price_per_category


def get_books_by_year(param_year):
    books = shop.models.Book.objects.filter(published_year__gt=param_year)

    return get_books_by_year


def count_books_by_price():
    counted_books = shop.models.Book.objects.annotate(book_count=Count("book__price"))

    return counted_books