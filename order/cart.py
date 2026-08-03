

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