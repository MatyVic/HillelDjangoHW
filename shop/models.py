from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Category name"))
    bio = models.TextField(default="No bio yet", verbose_name=_("bio"))

    def __str__(self):
        return self.name

    class Meta:
        permissions = [
            ("view_avg_price", "Can view average price per category"),
        ]

class Author(models.Model):
    first_name = models.CharField(max_length=100, verbose_name=_("First name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last name"))
    country = models.CharField(max_length=100, verbose_name=_("Country"))
    birth_date = models.DateField(default=timezone.now, verbose_name=_("Birth date"))
    bio = models.TextField(default="No bio yet", verbose_name=_("bio"))

    def __str__(self):
        return self.first_name + " " + self.last_name


class Publisher(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Publisher name"))
    country = models.CharField(max_length=100, verbose_name=_("Country"))
    website = models.URLField(verbose_name=_("Website"))
    bio = models.TextField(default="No bio yet", verbose_name=_("bio"))

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    author = models.ManyToManyField(Author, verbose_name=_("Author"))
    category = models.ManyToManyField(Category, verbose_name=_("Category"))
    publisher = models.ForeignKey('Publisher', on_delete=models.CASCADE, verbose_name=_("Publisher"))
    published_year = models.IntegerField(verbose_name=_("Published year"))
    added_at = models.DateTimeField(verbose_name=_("Added at"), default=timezone.now)
    amount = models.IntegerField(verbose_name=_("Amount"))
    price = models.IntegerField(verbose_name=_("Price"))
    available = models.BooleanField(default=True,verbose_name=_("Available"))
    calculated_rating = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name=_("Calculated rating"))

class Rating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name=_("Book"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User"))
    rating = models.IntegerField(verbose_name=_("Rating"))
    feedback = models.TextField(verbose_name=_("Feedback"))

    def get_absolute_url(self):
        return reverse("book", args=[self.book.id])