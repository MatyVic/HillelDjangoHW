from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.forms import IntegerField, Form
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from pip._internal import req

from order.form import NewOrderForm
from shop.models import Book

class AddBookForm(Form):
    book_id = IntegerField()
    quantity = IntegerField()

# Create your views here.

class NewOrderView(LoginRequiredMixin, View):

    def get(self, request):
        order_form = NewOrderForm()
        return render(request, "new_order.html", {"order_form": order_form})

    def post(self, request):
        order_form = NewOrderForm(request.POST)
        if order_form.is_valid():
            current_order = order_form.save(commit=False)
            current_order.user = request.user
            current_order.save()
            return HttpResponseRedirect("order_configuration.html")
        else:
            return render(request, "new_order.html", {"order_form": order_form})

class CartView(LoginRequiredMixin, View):

    def get(self, request):
        cart_data = request.session.get("cart", {})
        for book in cart_data:
            book.quantity = cart_data[book.book_id]
        return render(request, "cart.html", {"cart_data": cart_data})

    def post(self, request):
        form_data = request.POST
        cart_data = request.session.get("cart")
        if cart_data is None:
            request.session["cart"] = {}
        request.session["cart"].update({form_data["book_id"]: int(form_data["quantity"])})
        return redirect(request.args.get("next"))
