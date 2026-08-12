import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import override_settings
from django.urls import reverse

from shop.models import Book, Category, Rating, Publisher, Author

User = get_user_model()


# ==========================================
# Fixtures
# ==========================================

@pytest.fixture
def category(db):
    return Category.objects.create(name="Sci-Fi")


@pytest.fixture
def publisher(db):
    return Publisher.objects.create(name="Chilton Books")


@pytest.fixture
def author(db):
    return Author.objects.create(first_name="Frank", last_name="Herbert")


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="otheruser",
        email="other@example.com",
        password="password123"
    )


@pytest.fixture
def book(db, category, publisher, author):
    book_obj = Book.objects.create(
        title="Dune",
        price=300,
        amount=10,
        published_year=1965,
        publisher=publisher,
    )
    book_obj.category.add(category)
    book_obj.author.add(author)
    return book_obj


@pytest.fixture
def cheap_book(db, category, publisher):
    book_obj = Book.objects.create(
        title="Cheap Book",
        price=100,
        amount=5,
        published_year=2000,
        publisher=publisher,
    )
    book_obj.category.add(category)
    return book_obj


@pytest.fixture
def expensive_book(db, category, publisher):
    book_obj = Book.objects.create(
        title="Expensive Book",
        price=800,
        amount=2,
        published_year=2020,
        publisher=publisher,
    )
    book_obj.category.add(category)
    return book_obj


@pytest.fixture
def rating(db, user, book):
    return Rating.objects.create(
        user=user,
        book=book,
        rating=5,
        feedback="Great book!"
    )


# ==========================================
# Class-Based Views Tests
# ==========================================

@pytest.mark.django_db
class TestAllBooksView:
    def test_get_all_books_success(self, client, book, expensive_book):
        url = reverse("shop:all_books")
        response = client.get(url)

        assert response.status_code == 200
        assert "books" in response.context
        assert len(response.context["books"]) == 2
        assert response.templates[0].name == "books.html"

    def test_get_all_books_search_query(self, client, book, expensive_book):
        url = reverse("shop:all_books")
        response = client.get(url, {"q": "Dune"})

        assert response.status_code == 200
        assert len(response.context["books"]) == 1
        assert response.context["books"][0] == book


@pytest.mark.django_db
class TestAllCheapBooksView:
    def test_cheap_books_filter(self, client, cheap_book, expensive_book):
        url = reverse("shop:cheap_books")
        response = client.get(url)

        assert response.status_code == 200
        books = response.context["books"]
        assert cheap_book in books
        assert expensive_book not in books

    def test_cheap_books_search(self, client, cheap_book):
        url = reverse("shop:cheap_books")
        response = client.get(url, {"q": "Cheap"})

        assert response.status_code == 200
        assert len(response.context["books"]) == 1


class TestSpecificBookView:
    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_async_get_book(self, async_client, book):
        url = reverse("shop:book", kwargs={"book_id": book.pk})
        response = await async_client.get(url)

        assert response.status_code == 200
        assert response.context["object"] == book
        assert response.templates[0].name == "book.html"


@pytest.mark.django_db
class TestCreateFeedBackView:
    @override_settings(LOGIN_URL="/login/")
    def test_unauthenticated_redirects(self, client, book):
        url = reverse("shop:new_feedback", kwargs={"book_id": book.pk})
        response = client.get(url)

        assert response.status_code == 302
        assert "login" in response.headers.get("Location", "")

    def test_create_feedback_post(self, client, user, book):
        client.force_login(user)
        url = reverse("shop:new_feedback", kwargs={"book_id": book.pk})
        data = {"rating": 5, "feedback": "Amazing read!"}

        response = client.post(url, data)

        assert response.status_code == 302
        assert response.url == reverse("shop:book", kwargs={"book_id": book.id})
        assert Rating.objects.filter(book=book, feedback="Amazing read!").exists()


@pytest.mark.django_db
class TestFeedBackUpdateView:
    def test_owner_can_update_feedback(self, client, user, book, rating):
        client.force_login(user)
        url = reverse("shop:update_feedback", kwargs={"book_id": book.pk, "pk": rating.pk})
        data = {"rating": 4, "feedback": "Updated feedback"}

        response = client.post(url, data)

        assert response.status_code == 302
        rating.refresh_from_db()
        assert rating.rating == 4
        assert rating.feedback == "Updated feedback"

    def test_non_owner_forbidden(self, client, other_user, book, rating):
        client.force_login(other_user)
        url = reverse("shop:update_feedback", kwargs={"book_id": book.pk, "pk": rating.pk})

        response = client.get(url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestDeleteFeedBackView:
    def test_owner_can_delete_feedback(self, client, user, book, rating):
        client.force_login(user)
        url = reverse("shop:delete_feedback", kwargs={"book_id": book.pk, "pk": rating.pk})

        response = client.post(url)

        assert response.status_code == 302
        assert not Rating.objects.filter(pk=rating.pk).exists()

    def test_non_owner_cannot_delete(self, client, other_user, book, rating):
        client.force_login(other_user)
        url = reverse("shop:delete_feedback", kwargs={"book_id": book.pk, "pk": rating.pk})

        response = client.post(url)
        assert response.status_code == 403
        assert Rating.objects.filter(pk=rating.pk).exists()


# ==========================================
# Function-Based Views Tests
# ==========================================

@pytest.mark.django_db
def test_search_books(client, book):
    url = reverse("shop:search_books")

    response = client.get(url, {"q": "Herbert", "amount": 0})

    assert response.status_code == 200
    assert "books" in response.context
    assert book in response.context["books"]


@pytest.mark.django_db
def test_get_avg_price_per_category_without_permission(client, user):
    client.force_login(user)
    url = reverse("shop:avg_price")

    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_get_avg_price_per_category_with_permission(client, user, category):
    perm = Permission.objects.get(codename="view_avg_price")
    user.user_permissions.add(perm)
    client.force_login(user)

    url = reverse("shop:avg_price")
    response = client.get(url)

    assert response.status_code == 200
    assert "categories" in response.context


@pytest.mark.django_db
def test_get_books_by_year(client, book):
    url = reverse("shop:books_by_year")
    response = client.get(url, {"year": 1900})

    assert response.status_code == 200
    assert book in response.context["books"]


@pytest.mark.django_db
def test_count_books_by_price(client, category):
    url = reverse("shop:count_books")
    response = client.get(url)

    assert response.status_code == 200
    assert "categories" in response.context