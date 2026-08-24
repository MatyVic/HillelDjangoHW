from django.urls import path, include
from rest_framework import routers

from bookstore_api.views import BooksVeiewSet, AuthorsVeiewSet, CategorysVeiewSet, PublishersVeiewSet

router = routers.DefaultRouter()
router.register('books', BooksVeiewSet)
router.register('authors', AuthorsVeiewSet)
router.register('categories', CategorysVeiewSet)
router.register('publishers', PublishersVeiewSet)

app_name = "api"
urlpatterns = [
        path('', include(router.urls)),
    ]