from django.utils import timezone
from django.views.generic import ListView
from django.shortcuts import render
from django.db.models import Q, Avg, Count
from shop.models import Book, Category


class BookList(ListView):
    model = Book
    paginate_by = 100

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context



def get_cheap_books(request):
    cheap_books = Book.objects.filter(price__lt=5)
    return render(request, "my_template.html", {"books": cheap_books})


def search_books(request):
    search_text = request.GET.get("q", "")
    amount = request.GET.get("amount", 1)

    search_books_res = Book.objects.filter(
        Q(author__last_name__icontains=search_text) & Q(amount__gt=amount)
    ).distinct()
    return render(request, "my_template.html", {"books": search_books_res})


def get_avg_price_per_category(request):
    avg_price_per_category = Category.objects.annotate(avg_price=Avg("book__price"))
    return render(request, "avg_price.html", {"categories": avg_price_per_category})


def get_books_by_year(request):
    param_year = request.GET.get("year", 1800)
    books = Book.objects.filter(published_year__gt=param_year)
    return render(request, "my_template.html", {"books": books})


def count_books_by_price(request):
    counted_books = Category.objects.annotate(book_count=Count("book"))
    return render(request, "books_counter.html", {"categories": counted_books})
