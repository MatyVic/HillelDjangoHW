from django.contrib import admin

from shop.models import Book, Autor, Publisher, Category, Rating


class AuthorInline(admin.TabularInline):
    model = Book.author.through
    extra = 1

class CategoryInline(admin.TabularInline):
    model = Book.category.through
    extra = 1

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'show_autors', 'publisher',
                    'published_year', 'price', 'amount', 'calculated_rating', 'show_categories')
    list_filter = ('publisher', 'published_year', 'author', 'category')
    search_fields = ('title',
                     'author__first_name',
                     'author__last_name',
                     'publisher__name',
                     'published_year')
    inlines = [AuthorInline, CategoryInline]
    fieldsets = (
        (None, {"fields":
                    ('title',
                     'publisher',
                     'published_year',
                     'added_at',
                     'price',
                     'amount',
                     'available',
                     )}),
    )
    def show_autors(self, obj):
        return ", ".join([str(a) for a in obj.author.all()])
    show_autors.short_description = 'Autors'

    def show_categories(self, obj):
        return ", ".join([c.name for c in obj.category.all()])
    show_categories.short_description = 'Categories'


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'website')
    list_filter = ('country', 'website')
    search_fields = ('name', 'country', 'website')

    fieldsets = (
        (None, {"fields":
                    ('name',
                     'country',
                     'website',
                     'bio',
                     )}),
    )


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'country', 'birth_date')
    list_filter = ('first_name', 'last_name', 'country')
    search_fields = ('first_name', 'last_name', 'country')

    fieldsets = (
        (None, {"fields":('first_name',
                          'last_name',
                          'country',
                          'birth_date',
                          'bio',
                          )}),
    )


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rating')
    list_filter = ('book', 'user', 'rating')
    search_fields = ('book', 'user', 'rating')

    fieldsets = (
        (None, {"fields": ('book',
                           'user',
                           'rating',
                           'feedback',
                           )}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'bio')
    search_fields = ('name',)
    fieldsets = (
        (None, {"fields": ('name',
                           'bio',
                           )}),
    )
