import csv
import os
import logging
from datetime import datetime

import requests
from shop.models import Book
from django.conf import settings
from celery import shared_task

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


@shared_task(ignore_result=True)
def sync_stock_quantities():

    books = Book.objects.exclude(isbn__isnull=True).exclude(isbn="")

    for book in books:
        try:
            response = requests.get(
                f"{settings.WAREHOUSE_SERVICE_URL}/api/v1/stock/availability/",
                params={"isbn": book.isbn},
                timeout=5,
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            logger.warning("Warehouse timed out while syncing isbn=%s", book.isbn)
            continue
        except requests.exceptions.ConnectionError:
            logger.error("Warehouse unreachable while syncing isbn=%s", book.isbn)
            continue
        except requests.exceptions.RequestException:
            logger.exception("Unexpected error syncing isbn=%s", book.isbn)
            continue

        new_amount = response.json().get("total_quantity")
        if new_amount is not None and new_amount != book.amount:
            book.amount = new_amount
            book.available = new_amount > 0
            book.save(update_fields=["amount", "available"])
            logger.info("Updated amount for isbn=%s: %s", book.isbn, new_amount)
