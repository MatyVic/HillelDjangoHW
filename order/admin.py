from django.contrib import admin
from django.contrib.admin import TabularInline

from order.models import Order, OrderDetail


class OrderDetailAdmin(TabularInline):
    model = OrderDetail
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderDetailAdmin]
    list_display = ('owner', 'created_at', 'delivery_address',
                    'order_status', 'payment_status', 'ttn', 'total_price')
    list_filter = ('owner', 'created_at', 'delivery_address', 'order_status', 'payment_status')
    search_fields = ('owner', 'created_at', 'delivery_address', 'ttn')

    fieldsets = (
        (None, {"fields":
                    ('owner',
                     'created_at',
                     'delivery_address',
                     'order_status',
                     'payment_status',
                     'ttn',
                     'total_price',)}),
    )



