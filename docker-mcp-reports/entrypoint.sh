#!/bin/bash

case "$1" in
    "mcp")
        echo "Запуск GitHub Analytics MCP сервера..."
        exec python src/mcp_keepalive.py
        ;;
    "mcp-ai")
        echo "Запуск AI Advisor MCP сервера..."
        exec python src/ai_advisor_keepalive.py
        ;;
    "report")
        echo "Запуск генератора отчетов..."
        exec python src/main.py
        ;;
    "ai-test")
        echo "Тестирование AI Advisor..."
        exec python test_ai_advisor.py
        ;;
    *)
        echo "Использование: $0 {mcp|mcp-ai|report|ai-test}"
        echo "  mcp      - GitHub Analytics MCP сервер"
        echo "  mcp-ai   - AI Advisor MCP сервер"
        echo "  report   - Генератор отчетов"
        echo "  ai-test  - Тест AI Advisor"
        exit 1
        ;;
esac
