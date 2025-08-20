#!/usr/bin/env python3
"""
Тестовый файл для Python Runner MCP
"""

import sys
import os
from datetime import datetime

def main():
    print("=== Python Runner MCP Test ===")
    print(f"Время запуска: {datetime.now()}")
    print(f"Python версия: {sys.version}")
    print(f"Текущая директория: {os.getcwd()}")
    print(f"Аргументы командной строки: {sys.argv}")
    
    # Простой расчет
    result = 42 * 2
    print(f"Результат вычисления: 42 * 2 = {result}")
    
    print("=== Тест завершен ===")
    return result

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result == 84 else 1)
