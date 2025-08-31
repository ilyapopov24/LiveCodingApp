FROM python:3.11-slim

LABEL maintainer="MCP Report Generator"

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    curl \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh \
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

# Создаем директорию для загрузок с правильными правами
RUN mkdir -p /tmp/python_uploads && \
    chown -R appuser:appuser /tmp/python_uploads

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
