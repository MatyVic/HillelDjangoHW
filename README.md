# Bookstore — основний застосунок книжкового магазину (ProjectA)

Основний Django-застосунок інтернет-книгарні (вітрина, кошик, оформлення замовлень, оплата через Stripe). Обмінюється даними зі складським мікросервісом **ProjectB — Warehouse** через REST API: отримує нові книги зі складу і повідомляє про списання залишків після оплати замовлення.

## Архітектура

```mermaid
flowchart LR
    subgraph ProjectA["ProjectA — Bookstore (:8000)"]
        A_admin[Django Admin]
        A_shop[shop app]
        A_signal[post_save signal]
        A_task1[Celery: sync_stock_quantities]
        A_order[order app]
        A_success[order: success_handler]
    end

    subgraph ProjectB["ProjectB — Warehouse (:8001)"]
        B_admin[Django Admin]
        B_signal[post_save signal]
        B_task[Celery: sync_book_with_shop]
        B_api[DRF API: books / stock]
    end

    B_admin -->|"нова книга"| B_signal --> B_task
    B_task -->|"POST /api/v1/books/sync/"| A_shop
    A_signal --> A_task1
    A_task1 -->|"GET /api/v1/stock/availability/?isbn=..."| B_api
    A_success -->|"POST /api/v1/stock/deduct/"| B_api
    B_api --> DB_B[(PostgreSQL)]
    A_shop --> DB_A[(SQLite)]
```

Три напрямки міжсервісної комунікації:

| Напрямок | Тригер | Що відбувається |
|---|---|---|
| ProjectB → ProjectA | Нова книга створена на складі | Сигнал у ProjectB ставить Celery-таск у чергу → `POST /api/v1/books/sync/` у ProjectA → у `shop` створюється чернетка товару (`price=0`, `amount=0`, `available=False`) |
| ProjectA ← ProjectB | Періодичний Celery-таск `sync_stock_quantities` | ProjectA питає `GET /api/v1/stock/availability/?isbn=...` для кожної синхронізованої книги й оновлює кількість у себе |
| ProjectA → ProjectB | Успішна оплата замовлення (Stripe) | `order.success_handler` викликає `POST /api/v1/stock/deduct/`, щоб списати продану кількість зі складу |

> ⚠️ Точні назви ендпоінтів/таском викликів у `shop`/`order` наведені так, як вони описані з боку ProjectB. Якщо у вас інші назви — підкажіть, поправлю.

## Технології

- Django
- Django REST Framework (прийом `POST /api/v1/books/sync/` від ProjectB)
- SQLite (`db.sqlite3`)
- Celery (`sync_stock_quantities`, періодичний опитувальний таск)
- Stripe (оплата замовлень)
- Django Templates (вітрина, кошик, чекаут)

> ⚠️ Список орієнтовний — уточніть за `requirements.txt`/`settings.py`, якщо потрібна точна версія Django/DRF, брокер Celery (Redis?), JWT, i18n тощо — я не мав доступу до вмісту файлів репозиторію, лише до списку каталогів.

## Основні застосунки

- **bookstoreHW** — кореневий Django-проєкт (settings, urls, wsgi/asgi).
- **shop** — каталог книг, картки товару, кошик; приймає синхронізацію книг від ProjectB та періодично оновлює залишки.
- **order** — оформлення й обробка замовлень, інтеграція зі Stripe, `success_handler` після успішної оплати.
- **user_management** — кастомна модель користувача, реєстрація/логін/логаут.
- **templates** — спільні HTML-шаблони застосунку.

## Запуск

### 1. Клонувати і налаштувати оточення

```bash
git clone https://github.com/MatyVic/HillelDjangoHW.git
cd HillelDjangoHW
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Налаштувати змінні оточення

Створіть `.env` за зразком (уточніть повний список ключів — Stripe ключі, `SECRET_KEY`, URL ProjectB тощо):

```
DJANGO_SECRET_KEY=...
STRIPE_SECRET_KEY=...
STRIPE_PUBLISHABLE_KEY=...
WAREHOUSE_SERVICE_URL=http://localhost:8001
```

### 3. Мігрувати БД і запустити сервер

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8000
```

## Пов'язаний проєкт

**ProjectB — Warehouse** (`Warehouse_hillel_diploma`) — допоміжний мікросервіс складського обліку, з яким цей застосунок обмінюється даними.
