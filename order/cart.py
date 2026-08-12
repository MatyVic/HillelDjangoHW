from django.core.mail import EmailMultiAlternatives
from shop.models import Book

#AI reworked whole Cart class
class Cart:

    def __init__(self, request):
        self.request = request
        self.cart_data = request.session.setdefault("cart", {})

    @staticmethod
    def _parse_amount(amount):
        """Safely coerce user-supplied amount into a positive int, or None if invalid."""
        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return None
        return amount if amount > 0 else None

    def add_book(self, book_id, amount):
        book_id = str(book_id)
        amount = self._parse_amount(amount)
        if amount is None:
            return False  # invalid quantity, nothing added

        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return False

        current = self.cart_data.get(book_id, 0)
        new_amount = current + amount

        # Don't let the cart exceed available stock
        new_amount = min(new_amount, book.amount)
        if new_amount <= 0:
            return False

        self.cart_data[book_id] = new_amount
        self.request.session.modified = True
        return True

    def remove_book(self, book_id, amount=None):
        book_id = str(book_id)
        if book_id not in self.cart_data:
            return

        if amount is None:
            self.cart_data.pop(book_id, None)
        else:
            amount = self._parse_amount(amount)
            if amount is None:
                return  # invalid quantity, ignore silently (or raise, see note below)

            remaining = self.cart_data[book_id] - amount
            if remaining > 0:
                self.cart_data[book_id] = remaining
            else:
                self.cart_data.pop(book_id, None)

        self.request.session.modified = True

    def clear_cart(self):
        self.cart_data.clear()
        self.request.session.modified = True

    def get_total_items(self):
        return sum(self.cart_data.values())



class OrderEmailService:

    def __init__(self,  order, user):
        self.order = order
        self.user = user

    def send_confirmation_msg(self):
        subject = f"Замовлення №{self.order.id}"
        text_content = f"Ваше замовлення на суму {self.order.total_price} грн прийнято."
        html_content = f"""
        <p>Доброго дня, {self.user.username}!</p>
        <p>Ваше замовлення <strong>№{self.order.id}</strong> на суму 
        <strong>{self.order.total_price} грн</strong> успішно створено.</p>
        <p>Ми повідомимо вас про доставку.</p>
        """
        email = EmailMultiAlternatives(subject, text_content, None, [self.user.email or "test@example.com"])
        email.attach_alternative(html_content, "text/html")
        email.send()

    def send_error_msg(self):
        subject = "Помилка оплати"
        text_content = "Ваше замовлення не було підтверджене через помилку оплати."
        html_content = f"""
           <p>Доброго дня, {self.user.username}!</p>
           <p>На жаль, оплата не пройшла. Спробуйте ще раз або зверніться до підтримки.</p>
           """
        email = EmailMultiAlternatives(subject, text_content, None, [self.user.email or "test@example.com"])
        email.attach_alternative(html_content, "text/html")
        email.send()