# 1. Базовий образ з офіційного репозиторію Docker Hub
FROM python:3.12-slim

# 2. Налаштування змінних оточення для Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DB_HOST=docker_postgres \
    DB_PORT=5432


# 3. Встановлення робочої директорії всередині контейнера
WORKDIR /app

# 4. Копіювання файлу залежностей (окремий крок для кешування)
COPY requirements.txt .

# 5. Оновлення pip та встановлення бібліотек
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 6. Копіювання решти коду проєкту в контейнер
COPY . .

# 7. Команда для запуску вашого скрипту або сервера

# Порт, який слухає застосунок (наприклад, Flask/FastAPI)
EXPOSE 8000

# Команда запуску
CMD ["sh", "run_app.sh"]