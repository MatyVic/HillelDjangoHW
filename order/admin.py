from django.contrib import admin

from order.models import Order, OrderDetail

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
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

@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ('order', 'book', 'price', 'amount')
    list_filter = ('order', 'book')
    search_fields = ('order', 'book')

    fieldsets = (
        (None, {"fields":
                    ('order',
                     'book',
                     'price',
                     'amount',
                     )}),
    )

