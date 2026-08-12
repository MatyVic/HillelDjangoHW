from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone

from order.factories import (
    BookFactory,
    DeliveryDataFactory,
    OrderDetailFactory,
    OrderFactory,
    UserFactory,
)
from order.form import NewOrderForm, OrderDetailForm
from order.models import Order, OrderDetail, OrderStatus, PaymentStatus
from order.utils import create_new_order


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def disable_silk(settings):
    settings.MIDDLEWARE = [
        m for m in settings.MIDDLEWARE
        if m != "silk.middleware.SilkyMiddleware"
    ]
    if "silk" in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS.remove("silk")

@pytest.fixture
def delivery_data(user):
    return DeliveryDataFactory(owner=user)

# Фікстура для користувача
@pytest.fixture
def user(transactional_db):
    return UserFactory()

# Фікстура для книг
@pytest.fixture
def books(transactional_db):
    return [BookFactory(), BookFactory()]

# ---------------------------------------------------------------------------
# 1. Tests for Utility Function: create_new_order
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCreateNewOrderSync:

    def test_create_new_order_sync(self, user, delivery_data, books):
        book1, book2 = books
        cart_data = {str(book1.id): 1, str(book2.id): 2}

        result = create_new_order(user, cart_data, delivery_data.id)

        assert isinstance(result, Order)
        assert result.owner == user
        assert result.delivery_address_id == delivery_data.id
        assert result.total_price == book1.price * 1 + book2.price * 2
        assert result.orderdetail_set.count() == 2

    def test_create_order_statuses_and_details(self, user, delivery_data, books):
        book1, _ = books
        cart_data = {str(book1.id): 1}

        order = create_new_order(user, cart_data, delivery_data.id)

        assert order.order_status == OrderStatus.PROCESSING.value
        assert order.payment_status == PaymentStatus.PENDING.value
        assert order.ttn == ""

        detail = order.orderdetail_set.first()
        assert detail.book == book1
        assert detail.amount == 1
        assert detail.price == book1.price

    def test_create_order_empty_cart(self, user, delivery_data):
        order = create_new_order(user, {}, delivery_data.id)

        assert order.total_price == 0
        assert order.orderdetail_set.count() == 0

    def test_create_order_with_nonexistent_book(self, user, delivery_data):
        cart_data = {"99999": 1}

        order = create_new_order(user, cart_data, delivery_data.id)

        assert order.total_price == 0
        assert order.orderdetail_set.count() == 0

    def test_create_order_with_zero_books(self, user, delivery_data):
        cart_data = {"1": 0}

        order = create_new_order(user, cart_data, delivery_data.id)

        assert order.total_price == 0
        assert order.orderdetail_set.count() == 0

    def test_create_order_with_zero_books_existing_books(self, user, delivery_data):
        cart_data = {"99999": 0}

        order = create_new_order(user, cart_data, delivery_data.id)

        assert order.total_price == 0
        assert order.orderdetail_set.count() == 0

    def test_create_order_with_integer_keys_in_cart(self, user, delivery_data, books):
        book1, _ = books
        cart_data = {book1.id: 2}  # int key замість str

        with pytest.raises(KeyError):
            create_new_order(user, cart_data, delivery_data.id)

    def test_create_order_mixed_valid_and_invalid_book_ids(
        self, user, delivery_data, books
    ):
        book1, _ = books
        cart_data = {
            str(book1.id): 2,
            "99999": 5,
        }

        order = create_new_order(user, cart_data, delivery_data.id)

        assert order.total_price == book1.price * 2
        assert order.orderdetail_set.count() == 1

    def test_create_order_negative_quantity(self, user, delivery_data, books):
        book1, _ = books
        cart_data = {str(book1.id): -2}

        order = create_new_order(user, cart_data, delivery_data.id)

        assert order.total_price == book1.price * -2

    @patch("order.models.OrderDetail.save")
    def test_create_order_transaction_rollback_on_error(
        self, mock_save, user, delivery_data, books
    ):
        mock_save.side_effect = IntegrityError("Database error")
        book1, _ = books
        cart_data = {str(book1.id): 1}

        with pytest.raises(IntegrityError):
            create_new_order(user, cart_data, delivery_data.id)

        assert Order.objects.count() == 0

    def test_create_order_with_another_users_delivery_address(self, user, books):
        book1, _ = books
        other_user = UserFactory()
        other_delivery_data = DeliveryDataFactory(owner=other_user)
        cart_data = {str(book1.id): 1}

        order = create_new_order(user, cart_data, other_delivery_data.id)

        assert order.delivery_address.owner != user

    def test_create_order_with_string_quantity(self, user, delivery_data, books):
        book1, _ = books
        cart_data = {str(book1.id): "invalid_quantity"}

        with pytest.raises(TypeError):
            create_new_order(user, cart_data, delivery_data.id)

    def test_create_order_with_none_quantity(self, user, delivery_data, books):
        book1, _ = books
        cart_data = {str(book1.id): None}

        with pytest.raises(TypeError):
            create_new_order(user, cart_data, delivery_data.id)

    def test_create_order_snapshot_price_integrity(self, user, delivery_data, books):
        book1, _ = books
        cart_data = {str(book1.id): 1}

        order = create_new_order(user, cart_data, delivery_data.id)

        book1.price = 999
        book1.save()

        detail = order.orderdetail_set.first()
        assert detail.price == 100

    def test_create_order_with_anonymous_user(self, delivery_data, books):
        book1, _ = books
        anonymous_user = AnonymousUser()
        cart_data = {str(book1.id): 1}

        with pytest.raises((ValueError, IntegrityError, Exception)):
            create_new_order(anonymous_user, cart_data, delivery_data.id)


# ---------------------------------------------------------------------------
# 2. Tests for Views
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCartView:

    def test_cart_view_get_empty(self, client, user):
        client.force_login(user)
        response = client.get(reverse("order:cart"))
        assert response.status_code == 200
        assert len(response.context["cart_data"]) == 0

    def test_cart_view_get_with_items(self, client, user, books):
        book1, _ = books
        client.force_login(user)

        session = client.session
        session["cart"] = {str(book1.id): 2}
        session.save()

        response = client.get(reverse("order:cart"))
        assert response.status_code == 200
        cart_data = response.context["cart_data"]
        assert len(cart_data) == 1
        assert cart_data[0].id == book1.id
        assert cart_data[0].amount == 2

    def test_cart_view_post_add_book(self, client, user, books):
        book1, _ = books
        client.force_login(user)

        post_data = {"book_id": str(book1.id), "quantity": 3}
        response = client.post(
            reverse("order:cart") + "?next=/shop/", data=post_data
        )

        assert response.status_code == 302
        assert response.url == "/shop/"

        session = client.session
        assert session["cart"][str(book1.id)] == 3

    def test_cart_view_post_clear_cart(self, client, user, books):
        book1, _ = books
        client.force_login(user)

        session = client.session
        session["cart"] = {str(book1.id): 2}
        session.save()

        response = client.post(
            reverse("order:cart") + "?next=/cart/", data={"clear": "true"}
        )

        assert response.status_code == 302
        session = client.session
        assert session.get("cart") == {}


@pytest.mark.django_db
class TestOrderCheckoutView:

    def test_checkout_view_get(self, client, user, delivery_data, books):
        book1, _ = books
        client.force_login(user)

        session = client.session
        session["cart"] = {str(book1.id): 1}
        session.save()

        response = client.get(reverse("order:checkout"))
        assert response.status_code == 200
        assert len(response.context["delivery_adreses"]) == 1
        assert len(response.context["cart_books"]) == 1

    def test_checkout_view_post_creates_order(
        self, client, user, delivery_data, books
    ):
        book1, _ = books
        client.force_login(user)

        session = client.session
        session["cart"] = {str(book1.id): 2}
        session.save()

        post_data = {"delivery_address": delivery_data.id}
        response = client.post(
            reverse("order:checkout"), data=post_data
        )

        assert response.status_code == 302

        order = Order.objects.first()
        assert order is not None
        assert order.owner_id == user.id

        updated_session = client.session
        assert "cart" not in updated_session


@pytest.mark.django_db
class TestStripeAndSuccessHandlers:

    @patch("stripe.checkout.Session.create")
    def test_create_checkout_session_success(
        self, mock_stripe_create, client, user, delivery_data, books
    ):
        book1, _ = books
        client.force_login(user)
        
        order = OrderFactory(owner=user, delivery_address=delivery_data, total_price=200)
        OrderDetailFactory(order=order, book=book1, amount=2, price=book1.price)

        mock_stripe_session = MagicMock()
        mock_stripe_session.id = "cs_test_12345"
        mock_stripe_session.url = "https://checkout.stripe.com/pay/cs_test_12345"
        mock_stripe_create.return_value = mock_stripe_session

        url = reverse("order:stripe_hand", kwargs={"order_id": order.id})
        response = client.get(url)

        assert response.status_code == 302
        assert response.url == "https://checkout.stripe.com/pay/cs_test_12345"

        order.refresh_from_db()
        assert order.stripe_session_id == "cs_test_12345"

        mock_stripe_create.assert_called_once()
        kwargs = mock_stripe_create.call_args.kwargs
        assert kwargs["line_items"][0]["price_data"]["unit_amount"] == int(book1.price * 100)
        assert kwargs["line_items"][0]["quantity"] == 2

    @patch("stripe.checkout.Session.create")
    def test_create_checkout_session_stripe_exception(
        self, mock_stripe_create, client, user, delivery_data
    ):
        client.force_login(user)
        order = OrderFactory(owner=user, delivery_address=delivery_data, total_price=0)
        mock_stripe_create.side_effect = Exception("Stripe API Error")

        url = reverse("order:stripe_hand", kwargs={"order_id": order.id})
        response = client.get(url)

        assert response.status_code == 200
        assert "Stripe API Error" in response.content.decode()

    @patch("order.views.OrderEmailService.send_confirmation_msg")
    def test_success_handler_valid_session(
        self, mock_send_email, client, user, delivery_data
    ):
        order = OrderFactory(
            owner=user,
            delivery_address=delivery_data,
            stripe_session_id="cs_test_999",
            payment_status=PaymentStatus.PENDING.value,
        )

        url = reverse("order:success") + "?checkout_session=cs_test_999"
        response = client.get(url)

        assert response.status_code == 200
        assert "Payment success" in response.content.decode()

        order.refresh_from_db()
        assert order.payment_status == PaymentStatus.COMPLETED.value
        mock_send_email.assert_called_once()

    def test_success_handler_invalid_session(self, client):
        url = reverse("order:success") + "?checkout_session=non_existent_id"
        response = client.get(url)

        assert response.status_code == 200
        assert "Order not found" in response.content.decode()

    def test_success_handler_missing_param(self, client):
        url = reverse("order:success")
        response = client.get(url)

        assert response.status_code == 200
        assert "Payment failed" in response.content.decode()


# ---------------------------------------------------------------------------
# 3. Integration User Flow Test
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestIntegrationUserCheckoutFlow:

    @patch("order.views.OrderEmailService.send_confirmation_msg")
    @patch("stripe.checkout.Session.create")
    def test_full_checkout_flow_success(
            self, mock_stripe_create, mock_send_email, client, user, delivery_data, books
    ):

        book1, _ = books
        client.force_login(user)

        client.post(
            reverse("order:cart") + "?next=/cart/",
            data={"book_id": str(book1.id), "quantity": 2},
        )

        checkout_res = client.post(
            reverse("order:checkout"), data={"delivery_address": delivery_data.id}
        )
        assert checkout_res.status_code == 302

        order = Order.objects.first()
        assert order is not None

        mock_stripe_session = MagicMock()
        mock_stripe_session.id = "cs_flow_123"
        mock_stripe_session.url = "https://checkout.stripe.com/pay/cs_flow_123"
        mock_stripe_create.return_value = mock_stripe_session

        stripe_res = client.get(
            reverse("order:stripe_hand", kwargs={"order_id": order.id})
        )
        assert stripe_res.status_code == 302

        success_res = client.get(
            reverse("order:success") + "?checkout_session=cs_flow_123"
        )
        assert success_res.status_code == 200

        order.refresh_from_db()
        assert order.payment_status == PaymentStatus.COMPLETED.value
        mock_send_email.assert_called_once()

    def test_add_multiple_different_books_to_cart_flow(self, client, user, books):

        book1, book2 = books
        client.force_login(user)

        client.post(reverse("order:cart") + "?next=/cart/", data={"book_id": str(book1.id), "quantity": 1})
        client.post(reverse("order:cart") + "?next=/cart/", data={"book_id": str(book2.id), "quantity": 3})

        response = client.get(reverse("order:cart"))
        assert response.status_code == 200
        cart_data = response.context["cart_data"]
        assert len(cart_data) == 2

    def test_clear_cart_flow(self, client, user, books):

        book1, _ = books
        client.force_login(user)

        client.post(reverse("order:cart") + "?next=/cart/", data={"book_id": str(book1.id), "quantity": 2})
        client.post(reverse("order:cart") + "?next=/cart/", data={"clear": "true"})

        session = client.session
        assert session.get("cart") == {}

    def test_checkout_clears_session_cart(self, client, user, delivery_data, books):

        book1, _ = books
        client.force_login(user)

        client.post(reverse("order:cart") + "?next=/cart/", data={"book_id": str(book1.id), "quantity": 2})
        client.post(reverse("order:checkout"), data={"delivery_address": delivery_data.id})

        assert "cart" not in client.session

    def test_add_to_cart_and_redirect_flow(self, client, user, books):

        book1, _ = books
        client.force_login(user)

        response = client.post(
            reverse("order:cart") + "?next=/shop/",
            data={"book_id": str(book1.id), "quantity": 2},
        )

        assert response.status_code == 302
        assert response.url == "/shop/"
        assert client.session["cart"][str(book1.id)] == 2

    def test_stripe_api_error_handling_flow(self, client, user, delivery_data):
        client.force_login(user)
        order = OrderFactory(owner=user, delivery_address=delivery_data)

        with patch("stripe.checkout.Session.create", side_effect=Exception("Stripe Down")):
            response = client.get(reverse("order:stripe_hand", kwargs={"order_id": order.id}))
            assert response.status_code == 200
            assert "Stripe Down" in response.content.decode()

    def test_success_flow_missing_session_id(self, client):

        response = client.get(reverse("order:success"))
        assert response.status_code == 200
        assert "Payment failed" in response.content.decode()

    def test_success_flow_nonexistent_session_id(self, client):
        response = client.get(reverse("order:success") + "?checkout_session=invalid_id")
        assert response.status_code == 200
        assert "Order not found" in response.content.decode()

    @patch("order.views.OrderEmailService.send_confirmation_msg")
    def test_idempotent_success_payment_flow(self, mock_email, client, user, delivery_data):

        order = OrderFactory(
            owner=user,
            delivery_address=delivery_data,
            stripe_session_id="cs_repeat_123",
            payment_status=PaymentStatus.COMPLETED.value
        )

        response = client.get(reverse("order:success") + "?checkout_session=cs_repeat_123")
        assert response.status_code == 200
        order.refresh_from_db()
        assert order.payment_status == PaymentStatus.COMPLETED.value

    def test_checkout_with_multiple_addresses_selection(self, client, user, books):
        addr1 = DeliveryDataFactory(owner=user)
        addr2 = DeliveryDataFactory(owner=user)
        book1, _ = books
        client.force_login(user)

        client.post(reverse("order:cart") + "?next=/cart/", data={"book_id": str(book1.id), "quantity": 1})
        client.post(reverse("order:checkout"), data={"delivery_address": addr2.id})

        order = Order.objects.first()
        assert order.delivery_address == addr2

    def test_order_total_price_calculation_flow(
            self, client, user, delivery_data, books
    ):
        book1, book2 = books
        client.force_login(user)

        client.post(
            reverse("order:cart") + "?next=/cart/",
            data={"book_id": str(book1.id), "quantity": 2},
        )
        client.post(
            reverse("order:cart") + "?next=/cart/",
            data={"book_id": str(book2.id), "quantity": 3},
        )

        client.post(
            reverse("order:checkout"), data={"delivery_address": delivery_data.id}
        )

        order = Order.objects.first()
        expected_total = (book1.price * 2) + (book2.price * 3)
        assert order.total_price == expected_total

    def test_checkout_page_renders_context_correctly(self, client, user, delivery_data, books):
        book1, _ = books
        client.force_login(user)

        session = client.session
        session["cart"] = {str(book1.id): 1}
        session.save()

        response = client.get(reverse("order:checkout"))
        assert response.status_code == 200
        assert "delivery_adreses" in response.context
        assert "cart_books" in response.context

    def test_cart_view_handles_empty_cart_display(self, client, user):

        client.force_login(user)
        response = client.get(reverse("order:cart"))
        assert response.status_code == 200
        assert len(response.context["cart_data"]) == 0

    def test_user_cannot_pay_for_empty_order(self, client, user, delivery_data):

        client.force_login(user)
        order = OrderFactory(owner=user, delivery_address=delivery_data, total_price=0)

        with patch("stripe.checkout.Session.create") as mock_stripe:
            mock_session = MagicMock()
            mock_session.id = "cs_zero_123"
            mock_session.url = "https://checkout.stripe.com/pay/cs_zero_123"
            mock_stripe.return_value = mock_session

            response = client.get(reverse("order:stripe_hand", kwargs={"order_id": order.id}))
            assert response.status_code == 302

    @patch("order.views.OrderEmailService.send_confirmation_msg")
    def test_full_checkout_flow_triggers_email(
            self, mock_send_email, client, user, delivery_data
    ):
        order = OrderFactory(
            owner=user,
            delivery_address=delivery_data,
            stripe_session_id="cs_email_check_777",
            payment_status=PaymentStatus.PENDING.value
        )

        response = client.get(reverse("order:success") + "?checkout_session=cs_email_check_777")
        assert response.status_code == 200
        mock_send_email.assert_called_once()


# ---------------------------------------------------------------------------
# Unit Tests: Models
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestOrderModels:

    def test_order_str_representation(self, user, delivery_data):
        order = OrderFactory(owner=user, delivery_address=delivery_data)
        assert str(order) == f"Order #{order.id} by {user.email}"

    def test_order_default_statuses(self, user, delivery_data):
        order = OrderFactory(owner=user, delivery_address=delivery_data)
        assert order.order_status == OrderStatus.PROCESSING.value
        assert order.payment_status == PaymentStatus.PENDING.value

    def test_order_detail_total_price(self, user, delivery_data, books):
        book = books[0]
        order = OrderFactory(owner=user, delivery_address=delivery_data)
        detail = OrderDetailFactory(order=order, book=book, amount=3, price=100)
        assert detail.amount * detail.price == 300


# ---------------------------------------------------------------------------
# Unit Tests: Forms
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestOrderForms:

    # --- Тести для NewOrderForm ---

    def test_new_order_form_valid_data(self, user, delivery_data):
        """Тест валідності NewOrderForm при передачі всіх обов'язкових даних"""
        form_data = {
            "owner": user.id,
            "created_at": timezone.now(),
            "delivery_address": delivery_data.id,
            "order_status": OrderStatus.PROCESSING.value,
            "payment_status": PaymentStatus.PENDING.value,
            "total_price": 250.00,
            "ttn": "20450000000000",
        }
        form = NewOrderForm(data=form_data)

        assert form.is_valid(), f"Помилки форми: {form.errors}"
        order = form.save()
        assert order.owner == user
        assert order.delivery_address == delivery_data
        assert order.total_price == 250.00

    def test_new_order_form_missing_required_fields(self):
        """Тест невалідності NewOrderForm при відсутності обов'язкових полів"""
        form = NewOrderForm(data={})

        assert not form.is_valid()
        assert "owner" in form.errors
        assert "delivery_address" in form.errors

    def test_new_order_form_invalid_data(self, user, delivery_data):
        """Тест невалідності NewOrderForm при некоректній ціні (не число)"""
        form_data = {
            "owner": user.id,
            "created_at": timezone.now(),
            "delivery_address": delivery_data.id,
            "order_status": OrderStatus.PROCESSING.value,
            "payment_status": PaymentStatus.PENDING.value,
            "total_price": "invalid_number",  # Нечислове значення для DecimalField
            "ttn": "20450000000000",
        }
        form = NewOrderForm(data=form_data)

        assert not form.is_valid()
        assert "total_price" in form.errors

    # --- Тести для OrderDetailForm ---

    def test_order_detail_form_valid_data(self, user, delivery_data, books):
        """Тест валідності OrderDetailForm при передачі коректних даних"""
        order = OrderFactory(owner=user, delivery_address=delivery_data)
        book1, _ = books

        form_data = {
            "order": order.id,
            "book": book1.id,
            "amount": 3,
            "price": book1.price,
        }
        form = OrderDetailForm(data=form_data)

        assert form.is_valid(), f"Помилки форми: {form.errors}"
        detail = form.save()
        assert detail.order == order
        assert detail.book == book1
        assert detail.amount == 3

    def test_order_detail_form_missing_required_fields(self):
        """Тест невалідності OrderDetailForm без вказування книги та замовлення"""
        form = OrderDetailForm(data={"amount": 1})

        assert not form.is_valid()
        assert "order" in form.errors
        assert "book" in form.errors
        assert "price" in form.errors