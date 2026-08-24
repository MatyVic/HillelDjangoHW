from rest_framework import viewsets, serializers
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination

from order.models import Order, OrderDetail
from shop.models import Book, Author, Category, Publisher


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

class OrdersSerializer(serializers.ModelSerializer):
    items = OrderDetailSerializer(source="orderdetail_set", many=True, read_only=True)
    class Meta:
        model = Order
        fields = '__all__'

#Custom pagination
class BooksLimitOffsetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20

class BooksVeiewSet(viewsets.ModelViewSet):
    queryset = Book.objects.prefetch_related('author').prefetch_related('category').all()
    pagination_class = BooksLimitOffsetPagination
    serializer_class = BookSerializer


class AuthorsVeiewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorsSerializer


class CategorysVeiewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorysSerializer


class PublishersVeiewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublishersSerializer


class OrdersVeiewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrdersSerializer
