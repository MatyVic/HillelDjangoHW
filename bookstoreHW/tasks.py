from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives

User = get_user_model()

@shared_task(ignore_result=True)
def reg_mail_sender(user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return

    subject = f"Вітаємо {user.username}"
    text_content = f"Вітаємо {user.username}, реєстрація пройшла успішно"
    html_content = f"""
          <p>Доброго дня, {user.username}!</p>
          <p>Вітаємо з реєстрацією на сайті, надалі усі акції 
          та спецпропозиції будемо надсилати на цю адресу.</p>
          """
    email = EmailMultiAlternatives(subject, text_content, None, [user.email or "test@example.com"])
    email.attach_alternative(html_content, "text/html")
    email.send()
