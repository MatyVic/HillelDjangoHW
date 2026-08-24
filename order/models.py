from enum import Enum

from django.conf import settings
from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _

class OrderDetail(models.Model):
    book = models.ForeignKey('shop.Book', on_delete=models.CASCADE, verbose_name=_("Book"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    amount = models.IntegerField(verbose_name=_("Amount"))
    order = models.ForeignKey('Order', on_delete=models.CASCADE, verbose_name=_("Order"))


class OrderStatus(models.TextChoices):
    PROCESSING = 'PROCESSING', 'Processing'
    SHIPPED = 'SHIPPED', 'Shipped'
    DELIVERED = 'DELIVERED', 'Delivered'
    CANCELED = 'CANCELED', 'Canceled'

class PaymentStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PROCESSING = 'PROCESSING', 'Processing'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'


class PaymentMethod(Enum):
    CASH = 'CASH'
    CARD = 'CARD'


class Order(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Owner"))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Created at"))
    delivery_address = models.ForeignKey('user_management.DeliveryData', on_delete=models.CASCADE, verbose_name=_("Delivery Address"))
    total_price = models.DecimalField(max_digits=10, decimal_places=2,verbose_name=_("Total Price"))
    order_status = models.CharField(max_length=20,choices=OrderStatus.choices,default=OrderStatus.PROCESSING,verbose_name=_("Order Status"),)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING, verbose_name=_("Payment Status"),)
    ttn = models.CharField(max_length=50, verbose_name=_("TTN"))
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Stripe Session ID"))

    def __str__(self):
        return f"Order #{self.id} by {self.owner.email}"