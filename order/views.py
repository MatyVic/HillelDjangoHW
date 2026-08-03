import os

import stripe
from django.db import transaction

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import IntegerField, Form
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views import View


from order.cart import Cart, OrderEmailService
from order.form import NewOrderForm
from order.models import Order, OrderDetail, PaymentStatus, OrderStatus
from shop.models import Book
from user_management.models import DeliveryData


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
        cart = Cart(request)
        books = Book.objects.filter(pk__in=cart.cart_data.keys())
        for book in books:
            book.amount = cart.cart_data[str(book.id)]
        return render(request, "cart.html", {"cart_data": books})

    def post(self, request):
        form_data = request.POST
        cart = Cart(request)

        if "remove" in form_data:
            cart.remove_book(form_data["book_id"], form_data.get("quantity"))
        elif "clear" in form_data:
            cart.clear_cart()
        else:
            cart.add_book(form_data["book_id"], form_data["quantity"])

        return redirect(request.GET.get("next"))


class OrderChekoutView(LoginRequiredMixin, View):

    def get(self, request):
        cart_data = request.session.get("cart", {})
        books_to_order = Book.objects.filter(pk__in=list(cart_data.keys())).all()
        delivery_adreses = DeliveryData.objects.filter(owner=request.user)

        return render(request, "orderchekout.html",
                      {'delivery_adreses': delivery_adreses, 'cart_books': books_to_order})

    def post(self, request):
        cart_data = request.session.get("cart", {})
        with transaction.atomic():
            new_order = Order()
            new_order.owner = request.user
            new_order.order_status = OrderStatus.PROCESSING.value
            new_order.payment_status = PaymentStatus.PENDING.value
            new_order.ttn = ""
            new_order.total_price = 0
            new_order.delivery_address_id = request.POST.get("delivery_address")
            new_order.save()
            books_to_order = Book.objects.filter(pk__in=list(cart_data.keys())).all()
            for book in books_to_order:
                new_order.total_price += book.price * cart_data[str(book.id)]
                new_order_detail = OrderDetail()
                new_order_detail.order = new_order
                new_order_detail.book = book
                new_order_detail.amount = cart_data[str(book.id)]
                new_order_detail.price = book.price
                new_order_detail.save()
            new_order.save(update_fields=["total_price"])

        request.session.pop("cart", None)
        return redirect('order:stripe_hand', order_id=new_order.id)


def create_checkout_session(request, order_id):
    order = Order.objects.get(pk=order_id)
    order_details = OrderDetail.objects.select_related("book").filter(order=order)

    line_items = []
    for detail in order_details:
        line_items.append({
            'price_data': {
                'currency': 'uah',
                'product_data': {
                    'name': detail.book.title,
                },
                'unit_amount': int(detail.price * 100),
            },
            'quantity': detail.amount,
        })

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url='http://localhost:8000/order/success/?checkout_session={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:8000/order/error/?error=epayment_error',
        )

        order.stripe_session_id = session.id
        order.save(update_fields=["stripe_session_id"])
        return redirect(session.url)
    except Exception as e:
        return HttpResponse(str(e))


def success_handler(request):
    session_id = request.GET.get('checkout_session')  # правильна назва
    if session_id:
        try:
            current_order = Order.objects.get(stripe_session_id=session_id)
            current_order.payment_status = PaymentStatus.COMPLETED.value
            current_order.save()
            OrderEmailService(current_order, current_order.owner).send_confirmation_msg()
            return HttpResponse("Payment success")

        except Order.DoesNotExist:
            return HttpResponse("Order not found")
    else:
        return HttpResponse("Payment failed")
