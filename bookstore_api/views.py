from rest_framework import viewsets, serializers

from shop.models import Book, Author


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