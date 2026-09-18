# shop/warehouse_client.py
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def deduct_stock(isbn: str, quantity: int) -> bool:

    if not isbn:
        logger.warning("deduct_stock skipped: book has no isbn")
        return False

    url = f"{settings.WAREHOUSE_SERVICE_URL}/api/v1/stock/deduct/"

    try:
        response = requests.post(
            url, json={"isbn": isbn, "quantity": quantity}, timeout=5
        )
        response.raise_for_status()
        logger.info("Deducted %s unit(s) of isbn=%s from warehouse", quantity, isbn)
        return True
    except requests.exceptions.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 409:
            logger.error(
                "Warehouse reports insufficient stock for isbn=%s (requested %s): %s",
                isbn,
                quantity,
                exc.response.text,
            )
        else:
            logger.error("Warehouse rejected deduct request for isbn=%s: %s", isbn, exc)
    except requests.exceptions.Timeout:
        logger.warning("Warehouse service timed out while deducting isbn=%s", isbn)
    except requests.exceptions.ConnectionError:
        logger.error("Warehouse service unreachable while deducting isbn=%s", isbn)
    except requests.exceptions.RequestException:
        logger.exception("Unexpected error deducting stock for isbn=%s", isbn)

    return False
