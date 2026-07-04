from django import forms

from order.models import Order, OrderDetail


class NewOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'


class OrderDetailForm(forms.ModelForm):
    class Meta:
        model = OrderDetail
        fields = '__all__'
