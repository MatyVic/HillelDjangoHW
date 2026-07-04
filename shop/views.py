from django.contrib.auth.models import User
from django.shortcuts import render
from django.db.models import Q, Avg, Count
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from shop.models import Book, Category, Rating

# Class based views
class AllBooksView(ListView):
    model = Book
    template_name = "books.html"
    context_object_name = "books"

    def get_absolute_url(self):
        return reverse('book', kwargs={'pk': self.kwargs["book_id"]})

    def get_queryset(self):
        return Book.objects.prefetch_related("author", "category").all()

def get_cheap_books(request):
    cheap_books = Book.objects.filter(price__lt=5)
    return render(request, "my_template.html", {"books": cheap_books})

class SpecificBookView(DetailView):
    model = Book
    pk_url_kwarg = "book_id"
    template_name = "book.html"

class CreateFeedBackView(CreateView):
    model = Rating
    template_name = "feedback.html"
    fields = ['rating', 'feedback']

    def form_valid(self, form):
        form.instance.book = Book.objects.get(pk=self.kwargs["book_id"])
        User = get_user_model()
        form.instance.user = User.objects.get(pk=1)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("book", args=[self.object.book.id])


class FeedBackUpdateView(UpdateView):
    model = Rating
    template_name = "feedback_update.html"
    fields = ['rating', 'feedback']
    success_url = reverse_lazy('book')

    def form_valid(self, form):
        form.instance.book = Book.objects.get(pk=self.kwargs["book_id"])
        User = get_user_model()
        form.instance.user = User.objects.get(pk=1)
        return super().form_valid(form)

class DeleteFeedBackView(DeleteView):
    model = Rating
    template_name = "feedback_delete.html"

    def get_success_url(self):
        return reverse_lazy("book", args=[self.object.book.id])



# Function views
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
