import factory
from django.contrib.auth import get_user_model
from order.models import Order, OrderDetail, OrderStatus, PaymentStatus
from shop.models import Author, Category, Publisher, Book
from user_management.models import DeliveryData

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")


class DeliveryDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DeliveryData

    post_service = "Nova Poshta"
    post_service_branch = "Branch 1"
    city = "Kyiv"
    street = "Khreshchatyk 1"
    owner = factory.SubFactory(UserFactory)


class PublisherFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Publisher

    name = factory.Sequence(lambda n: f"Publisher {n}")
    country = "USA"
    website = "https://example.com"


class AuthorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Author

    first_name = "John"
    last_name = "Doe"
    country = "USA"

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book

    title = factory.Sequence(lambda n: f"Book {n}")
    publisher = factory.SubFactory(PublisherFactory)
    published_year = 2020
    amount = 10
    price = 100

    @factory.post_generation
    def author(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for author in extracted:
                self.author.add(author)

    @factory.post_generation
    def category(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for category in extracted:
                self.category.add(category)


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    owner = factory.SubFactory(UserFactory)
    delivery_address = factory.SubFactory(DeliveryDataFactory)
    total_price = 100
    order_status = OrderStatus.PROCESSING.value
    payment_status = PaymentStatus.PENDING.value


class OrderDetailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderDetail

    order = factory.SubFactory(OrderFactory)
    book = factory.SubFactory(BookFactory)
    amount = 1
    price = factory.SelfAttribute("book.price")