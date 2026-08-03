

class Cart:

    def __init__(self, request):
        self.request = request
        self.cart_data = request.session.get("cart", {})

    def add(self):
        pass


    def remove(self):
        pass


    def clear(self):
        pass
