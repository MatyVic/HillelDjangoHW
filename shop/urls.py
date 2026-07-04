from django.urls import path
from . import views
from .views import AllBooksView, SpecificBookView, CreateFeedBackView

urlpatterns = [
    path("cheap-books/", views.get_cheap_books, name="cheap_books"),
    path("search-books/", views.search_books, name="search_books"),
    path("avg-price/", views.get_avg_price_per_category, name="avg_price"),
    path("books-by-year/", views.get_books_by_year, name="books_by_year"),
    path("count-books/", views.count_books_by_price, name="count_books"),
    path("book/", AllBooksView.as_view(), name="book"),
    path("book/<int:book_id>", SpecificBookView.as_view(), name="book"),
    path("book/<int:book_id>/feedback", CreateFeedBackView.as_view(), name="new_feedback"),
    ]