from django.core.mail import EmailMultiAlternatives
from django.conf import settings


class Cart:

    def __init__(self, request):
        self.request = request
        self.cart_data = request.session.setdefault("cart", {})

    def add_book(self, book_id, amount):
        book_id = str(book_id)
        self.cart_data[book_id] = self.cart_data.get(book_id, 0) + int(amount)
        self.request.session.modified = True

    def remove_book(self, book_id, amount=None):
        book_id = str(book_id)
        if book_id not in self.cart_data:
            return

        if amount is None:
            self.cart_data.pop(book_id, None)
        else:
            remaining = self.cart_data[book_id] - int(amount)
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