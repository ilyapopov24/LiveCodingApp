#!/usr/bin/env python3
"""
Тест Python Runner MCP сервера
"""

import json
import sys
import os

# Добавляем путь к src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from python_runner_keepalive import PythonRunnerKeepaliveServer

def test_python_runner():
    """Тестирует Python Runner MCP сервер"""
    print("🧪 Тестируем Python Runner MCP сервер...")
    
    # Создаем сервер
    server = PythonRunnerKeepaliveServer()
    
    # Тест 1: Инициализация
    print("\n1️⃣ Тест инициализации:")
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test",
                "version": "1.0.0"
            }
        }
    }
    
    init_response = server.handle_request(init_request)
    print(f"Запрос: {json.dumps(init_request, ensure_ascii=False)}")
    print(f"Ответ: {json.dumps(init_response, ensure_ascii=False)}")
    
    # Тест 2: Список тулсов
    print("\n2️⃣ Тест списка тулсов:")
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }
    
    tools_response = server.handle_request(tools_request)
    print(f"Запрос: {json.dumps(tools_request, ensure_ascii=False)}")
    print(f"Ответ: {json.dumps(tools_response, ensure_ascii=False)}")
    
    # Тест 3: Вызов тулса
    print("\n3️⃣ Тест вызова тулса:")
    call_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "run-python-code",
            "arguments": {
                "code": "print('Hello, World!')"
            }
        }
    }
    
    call_response = server.handle_request(call_request)
    print(f"Запрос: {json.dumps(call_request, ensure_ascii=False)}")
    print(f"Ответ: {json.dumps(call_response, ensure_ascii=False)}")
    
    print("\n✅ Тест завершен!")

if __name__ == "__main__":
    test_python_runner()


