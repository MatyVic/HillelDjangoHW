from django.utils import timezone
from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(default="No bio yet")

    def __str__(self):
        return self.name


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    birth_date = models.DateField(default=timezone.now)
    bio = models.TextField(default="No bio yet")

    def __str__(self):
        return self.first_name + " " + self.last_name


class Publisher(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    website = models.URLField()
    bio = models.TextField(default="No bio yet")

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ManyToManyField(Author)
    category = models.ManyToManyField(Category)
    publisher = models.ForeignKey('Publisher', on_delete=models.CASCADE)
    published_year = models.IntegerField()
    added_at = models.DateTimeField()
    amount = models.IntegerField()
    price = models.IntegerField()
    available = models.BooleanField(default=True)
    calculated_rating = models.DecimalField(max_digits=5, decimal_places=2, null=True)

class Rating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField()
    feedback = models.TextField()

    def get_absolute_url(self):
        return reverse("book", args=[self.book.id])