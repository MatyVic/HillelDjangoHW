from celery import shared_task
from django.contrib.auth import get_user_model

from order.models import Order
from order.cart import OrderEmailService

User = get_user_model()


@shared_task(ignore_result=True)
def send_order_confirmation_email(order_id, user_id):
    try:
        order = Order.objects.get(pk=order_id)
        user = User.objects.get(pk=user_id)
    except (Order.DoesNotExist, User.DoesNotExist):
        return

    OrderEmailService(order, user).send_confirmation_msg()
