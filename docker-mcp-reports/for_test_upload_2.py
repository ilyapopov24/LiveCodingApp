#!/usr/bin/env python3
"""
Тестовый файл для проверки загрузки
"""

def add_numbers(a, b):
    """Складывает два числа"""
    return a + b

def multiply_numbers(a, b):
    """Умножает два числа"""
    return a * b

def is_even(number):
    """Проверяет, является ли число четным"""
    return number % 2 == 0

if __name__ == "__main__":
    print("Тестирование функций:")
    print(f"add_numbers(5, 3) = {add_numbers(5, 3)}")
    print(f"multiply_numbers(4, 7) = {multiply_numbers(4, 7)}")
    print(f"is_even(10) = {is_even(10)}")
    print(f"is_even(7) = {is_even(7)}")
