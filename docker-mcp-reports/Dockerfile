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

# Создаем директории для логов и данных
RUN mkdir -p logs data

# Создаем пользователя
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Переключаемся на пользователя
USER appuser

# Создаем простой entrypoint
RUN echo '#!/bin/bash\n\
if [ "$1" = "test" ]; then\n\
    echo "Запуск тестового режима..."\n\
    python src/main.py\n\
elif [ "$1" = "config" ]; then\n\
    echo "Проверка конфигурации..."\n\
    python -c "from config.config import Config; Config().print_config_summary()"\n\
elif [ "$1" = "manual" ]; then\n\
    echo "Запуск в ручном режиме..."\n\
    python src/main.py\n\
else\n\
    echo "Запуск в демон-режиме..."\n\
    echo "Для автоматического запуска используйте cron на хосте или systemd" \n\
    echo "Логи будут доступны в /app/logs/" \n\
    echo "Для остановки нажмите Ctrl+C" \n\
    \n\
    # Запускаем основной скрипт\n\
    python src/main.py\n\
fi' > /app/entrypoint.sh

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
