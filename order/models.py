from enum import Enum
from django.utils import timezone
from django.db import models


class OrderDetail(models.Model):
    book = models.ForeignKey('shop.Book', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.IntegerField()
    order = models.ForeignKey('Order', on_delete=models.CASCADE)


class PaymentStatus(Enum):
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'


class OrderStatus(Enum):
    PROCESSING = 'PROCESSING'
    SHIPPED = 'SHIPPED'
    DELIVERED = 'DELIVERED'
    CANCELED = 'CANCELED'


class PaymentMethod(Enum):
    CASH = 'CASH'
    CARD = 'CARD'


class Order(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    delivery_address = models.ForeignKey('user_management.DeliveryData', on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=20)
    payment_status = models.CharField(max_length=20)
    ttn = models.CharField(max_length=50)
