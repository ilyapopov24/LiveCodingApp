#!/usr/bin/env python3
"""
Тестовый скрипт для проверки тулсы test-python-code на научном калькуляторе
"""

import sys
import os

# Добавляем путь к src для импорта
sys.path.append('/app/src')

try:
    from python_runner_mcp_server import PythonRunnerMCPServer
    
    print("🚀 Инициализация Python Runner MCP Server...")
    
    # Создаем экземпляр сервера
    server = PythonRunnerMCPServer()
    
    print("✅ MCP Server инициализирован успешно")
    print(f"📋 Доступные тулсы: {len(server.list_tools())}")
    
    # Выводим список тулсов
    for tool in server.list_tools():
        print(f"  - {tool['name']}: {tool['description']}")
    
    print("\n🧪 Тестируем тулсу test-python-code на НАУЧНОМ КАЛЬКУЛЯТОРЕ...")
    
    # Тестируем тулсу test-python-code на сложном файле
    result = server.call_tool("test-python-code", {
        "file_path": "/host/test-project/scientific_calculator.py"
    })
    
    print("📊 Результат выполнения тулсы:")
    print("=" * 60)
    
    # Выводим результат
    if "content" in result and result["content"]:
        for content in result["content"]:
            if content.get("type") == "text":
                print(content["text"])
    else:
        print("❌ Неожиданный формат результата:")
        print(result)
    
    print("=" * 60)
    print("✅ Тестирование научного калькулятора завершено!")
    
except Exception as e:
    print(f"💥 Ошибка: {str(e)}")
    import traceback
    traceback.print_exc()



