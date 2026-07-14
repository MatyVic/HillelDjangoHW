# 1. Базовий образ з офіційного репозиторію Docker Hub
FROM python:3.12-slim

# 2. Налаштування змінних оточення для Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


# 3. Встановлення робочої директорії всередині контейнера
WORKDIR /app

# 4. Копіювання файлу залежностей (окремий крок для кешування)
COPY requirements.txt .

# 5. Оновлення pip та встановлення бібліотек
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 6. Копіювання решти коду проєкту в контейнер
COPY . .

# Порт, який слухає застосунок
EXPOSE 8000