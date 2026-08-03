

class Cart:

    def __init__(self, request):
        self.request = request
        self.cart_data = request.session.get("cart", {})

    def add_book(self, book_id, amount):
        self.request.session["cart"].update({book_id: int(amount)})


    def remove_book(self, book_id):
        self.request.session["cart"].pop(book_id)
        self.request.session.modified = True


    def clear_cart(self):
        pass
