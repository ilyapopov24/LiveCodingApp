#!/bin/bash

if [ "$1" = "mcp" ]; then
    echo "Запуск GitHub Analytics MCP сервера..." >&2
    exec python src/mcp_keepalive.py
elif [ "$1" = "mcp-ai" ]; then
    echo "Запуск AI Advisor MCP сервера..." >&2
    exec python src/ai_advisor_stdio_server.py
elif [ "$1" = "test" ]; then
    echo "Запуск тестового режима..."
    python src/main.py
elif [ "$1" = "config" ]; then
    echo "Проверка конфигурации..."
    python -c "from config.config import Config; Config().print_config_summary()"
elif [ "$1" = "manual" ]; then
    echo "Запуск в ручном режиме..."
    python src/main.py
elif [ "$1" = "mcp-test" ]; then
    echo "Тестирование MCP функциональности..."
    python src/mcp_server.py
elif [ "$1" = "ai-test" ]; then
    echo "Тестирование AI Advisor MCP сервера..."
    python test_ai_advisor.py
else
    echo "Запуск в демон-режиме..."
    echo "Для автоматического запуска используйте cron на хосте или systemd" 
    echo "Логи будут доступны в /app/logs/" 
    echo "Для остановки нажмите Ctrl+C" 
    echo ""
    echo "Доступные команды:"
    echo "  mcp       - Запуск GitHub Analytics MCP сервера для Cursor"
    echo "  mcp-ai    - Запуск AI Advisor MCP сервера для Cursor"
    echo "  mcp-test  - Тестирование MCP функциональности"
    echo "  ai-test   - Тестирование AI Advisor MCP сервера"
    echo "  test      - Тестовый режим"
    echo "  config    - Проверка конфигурации"
    echo "  manual    - Ручной режим"
    echo ""
    
    # Запускаем основной скрипт
    python src/main.py
fi
