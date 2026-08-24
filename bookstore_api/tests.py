
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from shop.models import Author, Category, Publisher, Book
from order.models import Order, OrderDetail, OrderStatus, PaymentStatus
from user_management.models import DeliveryData

User = get_user_model()


class BaseAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="AdminPass123!"
        )
        cls.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="UserPass123!"
        )
        cls.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="UserPass123!"
        )

        cls.category = Category.objects.create(name="Fiction", bio="Fiction books")
        cls.category2 = Category.objects.create(name="Science", bio="Science books")
        cls.author = Author.objects.create(
            first_name="Ernest", last_name="Hemingway", country="USA"
        )
        cls.publisher = Publisher.objects.create(
            name="Penguin", country="UK", website="https://penguin.co.uk"
        )

        cls.book = Book.objects.create(
            title="The Old Man and the Sea",
            publisher=cls.publisher,
            published_year=1952,
            amount=10,
            price=Decimal("12.50"),
            available=True,
        )
        cls.book.author.add(cls.author)
        cls.book.category.add(cls.category)

        cls.delivery1 = DeliveryData.objects.create(
            post_service="NovaPoshta",
            post_service_branch="Branch 1",
            city="Kyiv",
            street="Khreshchatyk 1",
            owner=cls.user1,
        )
        cls.delivery2 = DeliveryData.objects.create(
            post_service="NovaPoshta",
            post_service_branch="Branch 2",
            city="Lviv",
            street="Svobody 1",
            owner=cls.user2,
        )

        cls.order1 = Order.objects.create(
            owner=cls.user1,
            delivery_address=cls.delivery1,
            total_price=Decimal("12.50"),
            order_status=OrderStatus.PROCESSING,
            payment_status=PaymentStatus.PENDING,
            ttn="TTN-USER1-001",
        )
        OrderDetail.objects.create(
            book=cls.book, price=cls.book.price, amount=1, order=cls.order1
        )

        cls.order2 = Order.objects.create(
            owner=cls.user2,
            delivery_address=cls.delivery2,
            total_price=Decimal("12.50"),
            order_status=OrderStatus.SHIPPED,
            payment_status=PaymentStatus.COMPLETED,
            ttn="TTN-USER2-001",
        )
        OrderDetail.objects.create(
            book=cls.book, price=cls.book.price, amount=1, order=cls.order2
        )

    def setUp(self):
        # throttle counters live in cache; isolate every test from the others
        cache.clear()

    def auth(self, user):
        """Attach a JWT access token for `user` to self.client."""
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": user.username, "password": self._password_for(user)},
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    @staticmethod
    def _password_for(user):
        return "AdminPass123!" if user.username == "admin" else "UserPass123!"

class JWTAuthTests(BaseAPITestCase):

    def test_token_obtain_success(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "user1", "password": "UserPass123!"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_obtain_invalid_credentials(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "user1", "password": "wrong-password"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_success(self):
        obtain = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "user1", "password": "UserPass123!"},
        )
        refresh_token = obtain.data["refresh"]
        response = self.client.post(
            reverse("token_refresh"), {"refresh": refresh_token}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_token_refresh_invalid_token(self):
        response = self.client.post(
            reverse("token_refresh"), {"refresh": "not-a-real-token"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_verify_success(self):
        obtain = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "user1", "password": "UserPass123!"},
        )
        response = self.client.post(
            reverse("token_verify"), {"token": obtain.data["access"]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_verify_invalid_token(self):
        response = self.client.post(
            reverse("token_verify"), {"token": "garbage-token"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class BooksAPITests(BaseAPITestCase):
    list_url = "/api/v1/books/"

    def detail_url(self, pk):
        return f"/api/v1/books/{pk}/"

    def test_list_books_anonymous_allowed(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_book_returns_nested_author_and_category(self):
        response = self.client.get(self.detail_url(self.book.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data["author"], list)
        self.assertEqual(response.data["author"][0]["first_name"], "Ernest")
        self.assertIsInstance(response.data["category"], list)
        self.assertEqual(response.data["category"][0]["name"], "Fiction")

    def test_create_book_anonymous_forbidden(self):
        payload = {
            "title": "New Book",
            "publisher": self.publisher.pk,
            "published_year": 2020,
            "amount": 5,
            "price": "9.99",
            "author_ids": [self.author.pk],
            "category_ids": [self.category.pk],
        }
        response = self.client.post(self.list_url, payload)
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_create_book_authenticated_non_admin_forbidden(self):
        self.auth(self.user1)
        payload = {
            "title": "New Book",
            "publisher": self.publisher.pk,
            "published_year": 2020,
            "amount": 5,
            "price": "9.99",
            "author_ids": [self.author.pk],
            "category_ids": [self.category.pk],
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_book_admin_allowed(self):
        self.auth(self.admin)
        payload = {
            "title": "New Book",
            "publisher": self.publisher.pk,
            "published_year": 2020,
            "amount": 5,
            "price": "9.99",
            "author_ids": [self.author.pk],
            "category_ids": [self.category.pk],
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

    def test_update_book_admin_allowed(self):
        self.auth(self.admin)
        response = self.client.patch(self.detail_url(self.book.pk), {"price": "15.00"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.price, Decimal("15.00"))

    def test_delete_book_non_admin_forbidden(self):
        self.auth(self.user1)
        response = self.client.delete(self.detail_url(self.book.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_admin_allowed(self):
        self.auth(self.admin)
        response = self.client.delete(self.detail_url(self.book.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())

class CategoriesAPITests(BaseAPITestCase):
    list_url = "/api/v1/categories/"

    def detail_url(self, pk):
        return f"/api/v1/categories/{pk}/"

    def test_list_categories_anonymous_allowed(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_category_anonymous_forbidden(self):
        response = self.client.post(self.list_url, {"name": "Horror"})
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_create_category_non_admin_forbidden(self):
        self.auth(self.user1)
        response = self.client.post(self.list_url, {"name": "Horror"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_category_admin_allowed(self):
        self.auth(self.admin)
        response = self.client.post(self.list_url, {"name": "Horror"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_category_non_admin_forbidden(self):
        self.auth(self.user1)
        response = self.client.delete(self.detail_url(self.category.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())

class OrdersAPITests(BaseAPITestCase):
    list_url = "/api/v1/orders/"

    def detail_url(self, pk):
        return f"/api/v1/orders/{pk}/"

    def test_list_orders_requires_authentication(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_sees_only_own_orders(self):
        self.auth(self.user1)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        ids = {order["id"] for order in results}
        self.assertIn(self.order1.pk, ids)
        self.assertNotIn(self.order2.pk, ids)

    def test_admin_sees_all_orders(self):
        self.auth(self.admin)
        response = self.client.get(self.list_url)
        results = response.data.get("results", response.data)
        ids = {order["id"] for order in results}
        self.assertIn(self.order1.pk, ids)
        self.assertIn(self.order2.pk, ids)

    def test_owner_can_retrieve_own_order_with_nested_items(self):
        self.auth(self.user1)
        response = self.client.get(self.detail_url(self.order1.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(response.data["items"][0]["book"]["title"], self.book.title)

    def test_user_cannot_retrieve_others_order(self):
        self.auth(self.user1)
        response = self.client.get(self.detail_url(self.order2.pk))
        # order2 is excluded from user1's get_queryset() -> DRF returns 404, not 403
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_delete_others_order(self):
        self.auth(self.user1)
        response = self.client.delete(self.detail_url(self.order2.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Order.objects.filter(pk=self.order2.pk).exists())

class PaginationTests(BaseAPITestCase):

    def test_books_list_is_paginated(self):
        # create enough books to exceed a single page
        for i in range(25):
            book = Book.objects.create(
                title=f"Book {i}",
                publisher=self.publisher,
                published_year=2000 + i,
                amount=1,
                price=Decimal("5.00"),
            )
            book.author.add(self.author)
            book.category.add(self.category)

        response = self.client.get("/api/v1/books/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertLessEqual(len(response.data["results"]), 20)
        self.assertEqual(response.data["count"], Book.objects.count())

    def test_orders_pagination_has_next_link_when_needed(self):
        self.auth(self.admin)
        response = self.client.get("/api/v1/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

class FilteringTests(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.other_book = Book.objects.create(
            title="A Brief History of Time",
            publisher=self.publisher,
            published_year=1988,
            amount=3,
            price=Decimal("20.00"),
        )
        self.other_book.author.add(self.author)
        self.other_book.category.add(self.category2)

    def test_filter_books_by_category(self):
        response = self.client.get("/api/v1/books/", {"category": self.category2.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        titles = {b["title"] for b in results}
        self.assertIn("A Brief History of Time", titles)
        self.assertNotIn("The Old Man and the Sea", titles)

    def test_filter_books_by_available(self):
        self.other_book.available = False
        self.other_book.save()
        response = self.client.get("/api/v1/books/", {"available": True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        titles = {b["title"] for b in results}
        self.assertIn("The Old Man and the Sea", titles)
        self.assertNotIn("A Brief History of Time", titles)

    def test_filter_orders_by_status(self):
        self.auth(self.admin)
        response = self.client.get("/api/v1/orders/", {"order_status": "SHIPPED"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        statuses = {o["order_status"] for o in results}
        self.assertEqual(statuses, {"SHIPPED"})

class ThrottlingTests(BaseAPITestCase):

    def test_anonymous_requests_are_throttled_after_limit(self):
        for _ in range(60):
            response = self.client.get("/api/v1/books/")
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        response = self.client.get("/api/v1/books/")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)