import csv
import os
from datetime import datetime

from shop.models import Book

import logging

import requests
from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def generate_leftover_csv():
    leftover_data = Book.objects.filter(amount__gt=0).order_by("-id")
    report_dir = os.path.join(settings.BASE_DIR, "reports")
    os.makedirs(report_dir, exist_ok=True)

    filename = f"report_{datetime.now():%Y%m%d_%H%M%S}.csv"
    filepath = os.path.join(report_dir, filename)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Book ID", "Title", "Amount"])
        for book in leftover_data:
            writer.writerow([book.id, book.title, book.amount])

    return filepath


@shared_task(bind=True, max_retries=3, default_retry_delay=10, ignore_result=True)
def sync_book_with_warehouse(self, book_id):
    from shop.models import Book

    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        logger.warning("Book %s no longer exists, skipping sync", book_id)
        return

    if book.isbn:
        return  # вже синхронізовано

    payload = {
        "title": book.title,
        "authors": ", ".join(f"{a.first_name} {a.last_name}" for a in book.author.all())
        or "Unknown",
        "category": ", ".join(c.name for c in book.category.all()) or "Uncategorized",
        "publisher": book.publisher.name if book.publisher else "Unknown",
        "published_year": book.published_year,
    }
    try:
        response = requests.post(
            f"{settings.WAREHOUSE_SERVICE_URL}/api/v1/books/",
            json=payload,
            timeout=5,
        )
        response.raise_for_status()
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        logger.warning("Warehouse unreachable for book %s, retrying", book_id)
        raise self.retry(exc=None)
    except requests.exceptions.HTTPError as exc:
        logger.error("Warehouse rejected book %s: %s", book_id, exc.response.text)
        return

    isbn = response.json().get("isbn")
    if isbn:
        book.isbn = isbn
        book.save(update_fields=["isbn"])
        logger.info("Book %s synced, isbn=%s", book_id, isbn)
