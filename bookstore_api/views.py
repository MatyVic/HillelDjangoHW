from rest_framework import viewsets, serializers

from shop.models import Book, Author, Category, Publisher


class BooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BooksVeiewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BooksSerializer


class AuthorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class AuthorsVeiewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorsSerializer


class CategorysSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'

class CategorysVeiewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorysSerializer

class PublishersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'

class PublishersVeiewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublishersSerializer