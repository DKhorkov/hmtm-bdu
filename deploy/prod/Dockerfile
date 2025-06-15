# Основа для нашего docker-image
FROM python:3.12-slim

# Создание рабочей директории
WORKDIR /app

# Копирование зависимостей из корня проекта в корень рабочий директории /app:
COPY requirements-prod.txt .

# "Чистая" установка зависимостей:
RUN --mount=type=cache,target=/root/.cache \
    pip install --no-cache-dir -r requirements-prod.txt && \
    rm -rf /root/.cache/pip && \
    find /usr/local/lib -type d -name '__pycache__' -exec rm -rf {} +

# Копирование всего проекта (Относительно корня) в /app - контейнера:
COPY . .

# Локальный запуск сервиса
CMD ["python", "src/root/main.py"]
