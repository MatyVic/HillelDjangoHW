from django.urls import path

from order.views import NewOrderView, CartView, OrderChekoutView

app_name = "order"

urlpatterns = [
    path("new_order/", NewOrderView.as_view(), name="new_order"),
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/", OrderChekoutView.as_view(), name="order_chekout"),
]