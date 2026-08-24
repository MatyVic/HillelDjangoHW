from django.urls import path, include
from rest_framework import routers

from bookstore_api.views import BooksVeiewSet, AuthorsVeiewSet, CategorysVeiewSet, PublishersVeiewSet, OrdersVeiewSet

router = routers.DefaultRouter()
router.register('books', BooksVeiewSet , 'books')
router.register('authors', AuthorsVeiewSet , 'authors')
router.register('categories', CategorysVeiewSet, 'categories')
router.register('publishers', PublishersVeiewSet, 'publishers')
router.register('orders', OrdersVeiewSet, 'orders')
app_name = "api"
urlpatterns = [
        path('', include(router.urls)),
    ]