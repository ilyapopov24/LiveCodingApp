#!/bin/bash

case "$1" in
    "python-runner")
        echo "Запуск Python Runner MCP сервера..."
        exec python src/python_runner_keepalive.py
        ;;
    "python-runner-http")
        echo "Запуск Python Runner HTTP сервера..."
        exec python src/python_runner_http_server.py
        ;;
    "tunnel-server")
        echo "Запуск Python Runner Tunnel сервера..."
        exec python src/tunnel_server.py
        ;;
    "ollama-mcp")
        echo "Запуск Ollama MCP сервера..."
        exec python src/ollama_keepalive.py
        ;;
    *)
        echo "Использование: $0 {python-runner|python-runner-http|tunnel-server|ollama-mcp}"
        echo "  python-runner - Python Runner MCP сервер"
        echo "  python-runner-http - Python Runner HTTP сервер"
        echo "  tunnel-server - Python Runner Tunnel сервер"
        echo "  ollama-mcp - Ollama MCP сервер"
        exit 1
        ;;
esac
