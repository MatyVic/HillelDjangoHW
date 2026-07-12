from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.db.models import Q, Avg, Count
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import permission_required

from shop.models import Book, Category, Rating

#Mixin

# Class based views
class AllBooksView(ListView):
    model = Book
    template_name = "books.html"
    context_object_name = "books"
    paginate_by = 4

    def get_absolute_url(self):
        return reverse('book', kwargs={'pk': self.kwargs["book_id"]})

    def get_queryset(self):
        query = self.request.GET.get("q")
        qs = Book.objects.prefetch_related("author", "category").all()
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(author__last_name__icontains=query))
        return qs

class AllCheapBooksView(ListView):
    model = Book
    template_name = "books.html"
    context_object_name = "books"
    paginate = 4

    def get_queryset(self):
        query = self.request.GET.get("q")
        qs =  Book.objects.filter(price__lt=500).prefetch_related("author", "category")
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(author__last_name__icontains=query))
        return qs

class SpecificBookView(DetailView):
    model = Book
    pk_url_kwarg = "book_id"
    template_name = "book.html"

class CreateFeedBackView(LoginRequiredMixin, CreateView):
    model = Rating
    template_name = "feedback.html"
    fields = ['rating', 'feedback']

    def form_valid(self, form):
        form.instance.book = Book.objects.get(pk=self.kwargs["book_id"])
        user = get_user_model()
        form.instance.user = user.objects.get(pk=1)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("book", args=[self.object.book.id])

class EditDeleteByOwnerMixin:
    def dispatch(self, request, *args, **kwargs):
        rating = Rating.objects.filter(user=request.user, id=kwargs["pk"]).first()
        if rating:
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied

class FeedBackUpdateView(EditDeleteByOwnerMixin ,UpdateView):
    model = Rating
    template_name = "feedback_update.html"
    fields = ['rating', 'feedback']

    def form_valid(self, form):
        form.instance.book = Book.objects.get(pk=self.kwargs["book_id"])
        user = get_user_model()
        form.instance.user = user.objects.get(pk=1)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("book", args=[self.object.book.id])

class DeleteFeedBackView(EditDeleteByOwnerMixin, DeleteView):
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

@permission_required('books.view_avg_price', raise_exception=True)
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
