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
    "python-runner")
        echo "Запуск Python Runner MCP сервера..."
        exec python src/python_runner_keepalive.py
        ;;
    "spaceweb")
        echo "Запуск Spaceweb VPS MCP сервера..."
        exec python src/spaceweb_keepalive.py
        ;;
    *)
        echo "Использование: $0 {mcp|mcp-ai|report|ai-test|python-runner|spaceweb}"
        echo "  mcp           - GitHub Analytics MCP сервер"
        echo "  mcp-ai        - AI Advisor MCP сервер"
        echo "  report        - Генератор отчетов"
        echo "  ai-test       - Тест AI Advisor"
        echo "  python-runner - Python Runner MCP сервер"
        echo "  spaceweb      - Spaceweb VPS MCP сервер"
        exit 1
        ;;
esac
