# AI Code Review — HillelDjangoHW

Repo: https://github.com/MatyVic/HillelDjangoHW

Django bookstore project with three apps: `shop`, `order`, `user_management`. Overall a solid amount of functionality for a homework project, but there are some real bugs and security issues worth fixing.

## Strong points

- **Reasonable app separation** — `shop`, `order`, `user_management` are cleanly split by domain, each with its own models/views/urls.
- **Uses modern Django features well**: async views (`SpecificBookView`, `CartView`, `OrderChekoutView`), `select_related`/`prefetch_related` for query optimization, class-based generic views (ListView/CreateView/UpdateView/DeleteView) instead of reinventing CRUD.
- **i18n support** — `LocaleMiddleware`, `LANGUAGES`, `gettext_lazy` used consistently on model fields.
- **Structured logging** set up with `structlog` and rotating file handlers, split by app logger — more thought than most homework projects put into this.
- **Custom permission** (`view_avg_price`) and `@permission_required` used correctly for the analytics view — shows understanding of Django's auth/permissions system.
- **Stripe integration** for checkout, with an `OrderEmailService` abstraction for confirmation emails — good separation of concerns.
- **Decent test coverage in `order/tests.py`** (700 lines) — shows real effort testing the checkout flow.
- **Custom user model** (`AUTH_USER_MODEL`) set up from the start, which is the right call (much harder to retrofit later).

## Weak points

### Security issues (the important ones)

1. **Mass assignment on `NewOrderForm`** (`order/form.py`): `fields = '__all__'` on `Order` exposes `owner`, `order_status`, `payment_status`, and `stripe_session_id` directly to user input. A user could POST `payment_status=COMPLETED` and mark their own order paid.
2. **Bug compounding #1**: in `NewOrderView.post`, the code does `current_order.user = request.user` — but the `Order` model has no `user` field, only `owner`. This silently no-ops, meaning `owner` is left to whatever came from the form (see #1) instead of being force-set to the logged-in user.
3. **Payment confirmation trusts the client, not Stripe**: `success_handler` reads `checkout_session` from the URL query string and marks the order `COMPLETED` if any `Order` matches that `stripe_session_id` — with no verification against Stripe's API or a signed webhook. Anyone who can guess/enumerate a session id (or just replay their own) could hit `/order/success/?checkout_session=...` and mark an unpaid order as paid without a real payment check.
4. **`create_checkout_session` has no auth/ownership check** — any authenticated (or even anonymous, since the view has no `LoginRequiredMixin`) user who knows an `order_id` can generate a Stripe session for *someone else's* order (IDOR).
5. **Hardcoded feedback author**: in `CreateFeedBackView`/`FeedBackUpdateView`, `form.instance.user = user.objects.get(pk=1)` — every rating/feedback is attributed to user id 1, regardless of who's logged in. This directly contradicts `EditDeleteByOwnerMixin`, which checks `Rating.objects.filter(user=request.user, ...)` — since all ratings belong to user 1, only user 1 could ever edit/delete their own feedback.
6. **Open redirect** in `CartView.post`: `redirect(request.GET.get("next"))` with no validation that `next` is a safe, local URL.
7. **Secrets committed to the repo**: `SECRET_KEY` and the Postgres password are hardcoded in `settings.py` rather than pulled from environment/`.env`. Also `db.sqlite3` (and a stray `db.old____sqlite3`) are committed to source control.
8. **`DEBUG = True`** and `ALLOWED_HOSTS = []` are left as defaults — fine for local dev but a landmine if this ever gets deployed as-is.
9. **`django-silk` is enabled unconditionally** (`MIDDLEWARE` + `/silk/` urls) with no staff-only gate — this exposes SQL query profiling/request data to anyone who finds the URL.

### Design/correctness issues

- `Book.price` is an `IntegerField` — money should be `DecimalField` (as correctly done in `Order.total_price` and `OrderDetail.price`). Mixing the two is inconsistent and risks rounding bugs.
- `Rating.rating` has no validators (`MinValueValidator`/`MaxValueValidator`) — nothing stops a rating of -50 or 9999. There's also no `unique_together` on `(book, user)`, so a user could submit unlimited ratings for the same book.
- `Cart.add_book`/`remove_book` cast `amount` with `int(amount)` with no validation — a negative quantity or non-numeric string will either throw an uncaught exception or quietly corrupt the cart total. Cart quantities also aren't checked against `Book.amount` (stock) anywhere.
- Inconsistent naming: `AllCheapBooksView` sets `paginate = 4` instead of `paginate_by = 4` (a typo that silently disables pagination on that view, since Django's `ListView` looks specifically for `paginate_by`).
- `search_books`, `get_books_by_year` default `amount`/`year` to string/int literals compared against integer fields — works today but fragile, and unvalidated GET params flow straight into ORM filters.
- **Near-zero test coverage in `shop` and `user_management`** (3-line stub files) despite `order` being well tested — coverage is very lopsided.
- Minor: `AllBooksView.get_absolute_url` references `self.kwargs["book_id"]`, which doesn't exist on that view (it's a list view, not a detail view) — dead/broken code that's presumably never called, but worth removing.

## Suggested priority order for fixes

1. Fix the Stripe success handler to verify via Stripe's API (or a signed webhook) instead of trusting the query param.
2. Fix the `NewOrderForm` mass-assignment + the `owner` vs `user` typo — force `owner`/`order_status`/`payment_status` server-side, don't expose them on the form.
3. Fix the hardcoded `user pk=1` in feedback views — use `request.user`.
4. Move `SECRET_KEY`/DB credentials to environment variables and stop committing the sqlite files.
5. Add auth/ownership checks to `create_checkout_session`.
