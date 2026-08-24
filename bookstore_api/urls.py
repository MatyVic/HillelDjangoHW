from django.urls import path, include
from rest_framework import routers

from bookstore_api.views import BooksVeiewSet, AuthorsVeiewSet

router = routers.DefaultRouter()
router.register('books', BooksVeiewSet)
router.register('authors', AuthorsVeiewSet)

app_name = "api"
urlpatterns = [
        path('', include(router.urls)),
    ]