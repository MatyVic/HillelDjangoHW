python manage.py collectstatic --noinput
python manage.py migrate
gunicorn bookstoreHW.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 3