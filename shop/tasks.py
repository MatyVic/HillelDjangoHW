import csv
import os
from datetime import datetime

from celery import shared_task
from django.conf import settings

from shop.models import Book


@shared_task(ignore_result=True)
def generate_leftover_csv():
    leftover_data = Book.objects.filter(amount__gt=0).order_by("-id")
    report_dir = os.path.join(settings.BASE_DIR, "reports")
    os.makedirs(report_dir, exist_ok=True)

    filename = f"report_{datetime.now():%Y%m%d_%H%M%S}.csv"
    filepath = os.path.join(report_dir, filename)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Book ID","Title", "Amount"])
        for book in leftover_data:
            writer.writerow([book.id, book.title, book.amount])

    return filepath