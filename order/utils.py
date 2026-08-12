from django.db import transaction

from order.models import OrderStatus, PaymentStatus, Order, OrderDetail
from shop.models import Book


def create_new_order(self, user, cart_data, delivery_address_id):
    with transaction.atomic():
        new_order = Order()
        new_order.owner = user
        new_order.order_status = OrderStatus.PROCESSING.value
        new_order.payment_status = PaymentStatus.PENDING.value
        new_order.ttn = ""
        new_order.total_price = 0
        new_order.delivery_address_id = delivery_address_id
        new_order.save()
        books_to_order = Book.objects.filter(pk__in=list(cart_data.keys())).all()
        for book in books_to_order:
            new_order.total_price += book.price * cart_data[str(book.id)]
            new_order_detail = OrderDetail()
            new_order_detail.order = new_order
            new_order_detail.book = book
            new_order_detail.amount = cart_data[str(book.id)]
            new_order_detail.price = book.price
            new_order_detail.save()
        new_order.save(update_fields=["total_price"])

    return new_order
