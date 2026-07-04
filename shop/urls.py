from django.urls import path
from . import views
from .views import AllBooksView, SpecificBookView, CreateFeedBackView, FeedBackUpdateView, DeleteFeedBackView,AllCheapBooksView

app_name = "shop"
urlpatterns = [
    path("cheap-books/", AllCheapBooksView.as_view(), name="cheap_books"),
    path("search-books/", views.search_books, name="search_books"),
    path("avg-price/", views.get_avg_price_per_category, name="avg_price"),
    path("books-by-year/", views.get_books_by_year, name="books_by_year"),
    path("count-books/", views.count_books_by_price, name="count_books"),
    path("", AllBooksView.as_view(), name="all_books"),
    path("book/<int:book_id>", SpecificBookView.as_view(), name="book"),
    path("book/<int:book_id>/feedback/", CreateFeedBackView.as_view(), name="new_feedback"),
    path("book/<int:book_id>/feedback/<int:pk>/", FeedBackUpdateView.as_view(), name="update_feedback"),
    path("book/<int:book_id>/feedback/<int:pk>/delete", DeleteFeedBackView.as_view(), name="delete_feedback"),
    ]