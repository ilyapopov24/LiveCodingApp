#!/usr/bin/env python3
"""
Тестовый файл для проверки тулсы test-python-code
Содержит простые математические функции
"""

def add_numbers(a: float, b: float) -> float:
    """Складывает два числа"""
    return a + b

def multiply_numbers(a: float, b: float) -> float:
    """Умножает два числа"""
    return a * b

def is_even(number: int) -> bool:
    """Проверяет, является ли число четным"""
    return number % 2 == 0

def calculate_factorial(n: int) -> int:
    """Вычисляет факториал числа"""
    if n < 0:
        raise ValueError("Факториал не определен для отрицательных чисел")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def find_max(numbers: list) -> float:
    """Находит максимальное число в списке"""
    if not numbers:
        raise ValueError("Список не может быть пустым")
    return max(numbers)

if __name__ == "__main__":
    print("🧮 Тестирование функций калькулятора:")
    print(f"add_numbers(5, 3) = {add_numbers(5, 3)}")
    print(f"multiply_numbers(4, 7) = {multiply_numbers(4, 7)}")
    print(f"is_even(10) = {is_even(10)}")
    print(f"is_even(7) = {is_even(7)}")
    print(f"calculate_factorial(5) = {calculate_factorial(5)}")
    print(f"find_max([1, 5, 3, 9, 2]) = {find_max([1, 5, 3, 9, 2])}")




