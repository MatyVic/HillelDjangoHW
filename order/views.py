import os

import stripe
stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import IntegerField, Form
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views import View


from order.cart import Cart
from order.form import NewOrderForm
from order.models import Order, OrderDetail, PaymentStatus
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

        return render(request, "orderchekout.html", {'delivery_adreses': delivery_adreses, 'cart_books': books_to_order})

    def post(self, request):
        cart_data = request.session.get("cart", {})
        new_order = Order()
        new_order.owner = request.user
        new_order.save(commit=False)
        books_to_order = Book.objects.filter(pk__in=list(cart_data.keys())).all()
        for book in books_to_order:
            new_order.total_price += book.price * cart_data[str(book.id)]
            new_order_detail = OrderDetail()
            new_order_detail.order = new_order
            new_order_detail.book = book
            new_order_detail.amount = cart_data[str(book.id)]
            new_order_detail.save()

        new_order.save(commit=True)

        request.session.pop("cart")
        #return render(request, "orderchekout.html", {"new_order": new_order})
        return redirect('order:stripe_hand')


def create_checkout_session(request):
    try:
        # Create a new checkout session object
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Premium Subscription T-Shirt',
                        },
                        'unit_amount': 2000,  # Amount in cents ($20.00)
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',  # Use 'subscription' for recurring payments
            success_url='http://localhost:8000/?chekout_session={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:8000/?error=epayment_error',
        )

        # This URL redirects the user to the Stripe-hosted payment form
        user = request.user
        currect_order = Order.objects.get(user=user, payment_status = 'pending')
        currect_order.stripe_session_id = session.id
        currect_order.save()
        return redirect(session.url)
    except Exception as e:
        return HttpResponse(str(e))


def success_handler(request):
    session_id = request.Get.get('chekout_session')
    if session_id:
        currect_order = Order.objects.get(stripe_session_id=session_id)
        currect_order.payment_status = PaymentStatus.COMPLETED
        currect_order.save()
        return HttpResponse("Payment success")
    else:
        return HttpResponse("Payment failed")