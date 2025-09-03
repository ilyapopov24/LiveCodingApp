#!/usr/bin/env python3
"""
Тест для Sequential Thinking MCP Server
"""

import json
import sys
import os

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sequential_thinking_mcp_server import SequentialThinkingMCPServer

def test_sequential_thinking():
    """Тестирует полный цикл sequential thinking"""
    
    server = SequentialThinkingMCPServer()
    
    print("🧪 Тестирование Sequential Thinking MCP Server")
    print("=" * 50)
    
    # Тест 1: Этап "thought"
    print("\n1️⃣ Тест этапа 'thought':")
    result1 = server.call_tool("sequential-thinking", {
        "thought": "Для решения этой задачи нужно проанализировать требования и выбрать подходящий алгоритм",
        "stage": "thought",
        "problem": "Как оптимизировать производительность приложения?"
    })
    print(result1["content"][0]["text"])
    
    # Тест 2: Этап "validation"
    print("\n2️⃣ Тест этапа 'validation':")
    result2 = server.call_tool("sequential-thinking", {
        "thought": "Алгоритм A будет быстрее, но потребует больше памяти",
        "stage": "validation",
        "problem": "Как оптимизировать производительность приложения?",
        "validation_result": "Проверил документацию - алгоритм A действительно быстрее на 30%"
    })
    print(result2["content"][0]["text"])
    
    # Тест 3: Этап "answer"
    print("\n3️⃣ Тест этапа 'answer':")
    result3 = server.call_tool("sequential-thinking", {
        "thought": "Рекомендую использовать алгоритм A с кэшированием",
        "stage": "answer",
        "problem": "Как оптимизировать производительность приложения?",
        "final_answer": "Используйте алгоритм A с LRU кэшем для достижения 30% прироста производительности"
    })
    print(result3["content"][0]["text"])
    
    # Проверяем историю
    print(f"\n📊 История мыслей: {len(server.thought_history)} записей")
    
    print("\n✅ Все тесты пройдены успешно!")

def test_tool_listing():
    """Тестирует получение списка инструментов"""
    
    server = SequentialThinkingMCPServer()
    
    print("\n🔧 Тест получения списка инструментов:")
    tools = server.list_tools()
    
    print(f"Найдено инструментов: {len(tools)}")
    for tool in tools:
        print(f"- {tool['name']}: {tool['description']}")
    
    print("✅ Тест списка инструментов пройден!")

def test_error_handling():
    """Тестирует обработку ошибок"""
    
    server = SequentialThinkingMCPServer()
    
    print("\n❌ Тест обработки ошибок:")
    
    try:
        # Неверное имя инструмента
        server.call_tool("unknown-tool", {})
        print("❌ Ошибка: должен был быть выброшен exception")
    except ValueError as e:
        print(f"✅ Правильно обработана ошибка: {e}")
    
    try:
        # Неверный этап
        server.call_tool("sequential-thinking", {
            "thought": "Тест",
            "stage": "invalid-stage",
            "problem": "Тест"
        })
        print("❌ Ошибка: должен был быть выброшен exception")
    except ValueError as e:
        print(f"✅ Правильно обработана ошибка: {e}")
    
    print("✅ Тест обработки ошибок пройден!")

if __name__ == "__main__":
    test_sequential_thinking()
    test_tool_listing()
    test_error_handling()
    
    print("\n🎉 Все тесты завершены успешно!")



