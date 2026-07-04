from django.urls import path

from order.views import NewOrderView

app_name = "order"

urlpatterns = [
    path("new_order/", NewOrderView.as_view(), name="new_order"),
]