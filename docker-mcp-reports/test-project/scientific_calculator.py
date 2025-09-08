#!/usr/bin/env python3
"""
Научный калькулятор для тестирования Python Runner MCP сервера
"""

import math
import sys

def main():
    """Главная функция калькулятора"""
    print("🧮 Научный калькулятор")
    print("=" * 30)
    
    # Простые вычисления
    result1 = 2 + 2
    print(f"2 + 2 = {result1}")
    
    result2 = 10 * 5
    print(f"10 * 5 = {result2}")
    
    result3 = 100 / 4
    print(f"100 / 4 = {result3}")
    
    # Научные функции
    result4 = math.sqrt(16)
    print(f"√16 = {result4}")
    
    result5 = math.sin(math.pi / 2)
    print(f"sin(π/2) = {result5}")
    
    result6 = math.log(10)
    print(f"ln(10) = {result6}")
    
    result7 = math.pow(2, 3)
    print(f"2³ = {result7}")
    
    # Сложные вычисления
    result8 = math.sqrt(2) * math.pi
    print(f"√2 × π = {result8}")
    
    result9 = math.factorial(5)
    print(f"5! = {result9}")
    
    result10 = math.gcd(48, 18)
    print(f"НОД(48, 18) = {result10}")
    
    print("=" * 30)
    print("✅ Все вычисления выполнены успешно!")

if __name__ == "__main__":
    main()

