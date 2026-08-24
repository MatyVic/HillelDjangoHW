from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, serializers
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination

from order.models import Order, OrderDetail, OrderStatus, PaymentStatus
from shop.models import Book, Author, Category, Publisher
from user_management.models import DeliveryData


class PublishersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'

class AuthorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class CategorysSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    author = AuthorsSerializer(many=True, read_only=True)
    category = CategorysSerializer(many=True, read_only=True)
    author_ids = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(), source="author", many=True, write_only=True
    )
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", many=True, write_only=True
    )
    class Meta:
        model = Book
        fields = '__all__'

class OrderDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    class Meta:
        model = OrderDetail
        fields = ["id", "book", "price", "amount"]


class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryData
        fields = '__all__'

class OrdersSerializer(serializers.ModelSerializer):
    items = OrderDetailSerializer(source="orderdetail_set", many=True, read_only=True)
    delivery_address = DeliveryAddressSerializer(read_only=True)
    class Meta:
        model = Order
        fields = '__all__'

#Custom pagination
class BooksLimitOffsetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20

#Custom Throttle
class OrderCustomThrottle(LimitOffsetPagination):
    scope = 'order_throttle'

class BooksVeiewSet(viewsets.ModelViewSet):
    queryset = Book.objects.prefetch_related('author').prefetch_related('category').all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = BooksLimitOffsetPagination
    filterset_fields = ['author', 'title', 'category', 'publisher', 'published_year', 'available']


class AuthorsVeiewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [ 'first_name', 'last_name' , 'country', 'birth_date']


class CategorysVeiewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorysSerializer
    filter_backends = [DjangoFilterBackend]


class PublishersVeiewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublishersSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'country', 'website',]


class OrdersVeiewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrdersSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['owner', 'delivery_address', 'order_status', 'payment_status', 'ttn']
    throttle_classes = [OrderCustomThrottle]
