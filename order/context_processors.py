from order.cart import Cart

def cart_count(request):
    if request.user.is_authenticated:
        return {"cart_items_count": Cart(request).get_total_items()}
    return {"cart_items_count": 0}