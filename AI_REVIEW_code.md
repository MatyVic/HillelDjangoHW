## Before AI

`shop/models.py`
```python
class Book(models.Model):
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    author = models.ManyToManyField(Author, verbose_name=_("Author"))
    category = models.ManyToManyField(Category, verbose_name=_("Category"))
    publisher = models.ForeignKey('Publisher', on_delete=models.CASCADE, verbose_name=_("Publisher"))
    published_year = models.IntegerField(verbose_name=_("Published year"))
    added_at = models.DateTimeField(verbose_name=_("Added at"), default=timezone.now)
    amount = models.IntegerField(verbose_name=_("Amount"))
    price = models.IntegerField(verbose_name=_("Price"))
    available = models.BooleanField(default=True, verbose_name=_("Available"))
    calculated_rating = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name=_("Calculated rating"))
```

`shop/models.py`
```python
class Rating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name=_("Book"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User"))
    rating = models.IntegerField(verbose_name=_("Rating"))
    feedback = models.TextField(verbose_name=_("Feedback"))

    def get_absolute_url(self):
        return reverse("book", args=[self.book.id])
```

`order/cart.py`
```python
class Cart:

    def __init__(self, request):
        self.request = request
        self.cart_data = request.session.setdefault("cart", {})

    def add_book(self, book_id, amount):
        book_id = str(book_id)
        self.cart_data[book_id] = self.cart_data.get(book_id, 0) + int(amount)
        self.request.session.modified = True

    def remove_book(self, book_id, amount=None):
        book_id = str(book_id)
        if book_id not in self.cart_data:
            return

        if amount is None:
            self.cart_data.pop(book_id, None)
        else:
            remaining = self.cart_data[book_id] - int(amount)
            if remaining > 0:
                self.cart_data[book_id] = remaining
            else:
                self.cart_data.pop(book_id, None)

        self.request.session.modified = True
    def clear_cart(self):
        self.cart_data.clear()
        self.request.session.modified = True

    def get_total_items(self):
        return sum(self.cart_data.values())

```
