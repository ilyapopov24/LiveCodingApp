FROM python:3.11-slim

LABEL maintainer="MCP Report Generator"

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY src/ ./src/
COPY config/ ./config/
COPY test_ai_advisor.py ./test_ai_advisor.py
COPY test_calculator.py ./test_calculator.py

# Копируем переменные окружения
COPY docker-keys.env ./docker-keys.env
COPY docker-settings.env ./docker-settings.env

# Создаем директории для логов и данных
RUN mkdir -p logs data

# Копируем entrypoint
COPY entrypoint.sh /app/entrypoint.sh

# Создаем пользователя
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Переключаемся на пользователя
USER appuser

# Делаем entrypoint исполняемым
RUN chmod +x /app/entrypoint.sh

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Volumes для логов и данных
VOLUME ["/app/logs", "/app/data"]

# Expose порт (если понадобится)
EXPOSE 8000

# Entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# По умолчанию запускаем в демон-режиме
CMD ["daemon"]
