#!/bin/bash

case "$1" in
    "python-runner-http")
        echo "Запуск Python Runner HTTP сервера..."
        exec python src/python_runner_http_server.py
        ;;
    "tunnel-server")
        echo "Запуск Python Runner Tunnel сервера..."
        exec python src/tunnel_server.py
        ;;
    *)
        echo "Использование: $0 {python-runner-http|tunnel-server}"
        echo "  python-runner-http - Python Runner HTTP сервер"
        echo "  tunnel-server - Python Runner Tunnel сервер"
        exit 1
        ;;
esac
