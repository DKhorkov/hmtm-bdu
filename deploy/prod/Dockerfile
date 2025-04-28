# Основа для нашего docker-image
FROM python:3.12-slim
LABEL authors='sam'

# Создание рабочей директории
WORKDIR /app

# Копирование зависимостей из корня проекта в корень рабочий директории /app:
COPY requirements.txt .

# "Чистая" установка зависимостей:
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt && \
    pip cache purge && \
    find /usr/local/lib -name '__pycache__' -exec rm -rf {} +

# Копирование всего проекта (Относительно корня) в /app - контейнера:
COPY . .

# Локальный запуск сервиса
CMD ["python", "src/main.py"]
