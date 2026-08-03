from django.urls import path

from order.views import NewOrderView, CartView, OrderChekoutView, create_checkout_session, success_handler

app_name = "order"

urlpatterns = [
    path("new_order/", NewOrderView.as_view(), name="new_order"),
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/", OrderChekoutView.as_view(), name="order_chekout"),
    path("stripe/", create_checkout_session, name="stripe_hand"),
    path("success/", success_handler, name="stripe_success"),
]