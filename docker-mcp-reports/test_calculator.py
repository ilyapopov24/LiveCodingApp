#!/usr/bin/env python3
"""
Простой калькулятор для тестирования тулсы test-python-code
"""

def add(a, b):
    """Складывает два числа"""
    return a + b

def subtract(a, b):
    """Вычитает второе число из первого"""
    return a - b

def multiply(a, b):
    """Умножает два числа"""
    return a * b

def divide(a, b):
    """Делит первое число на второе"""
    if b == 0:
        raise ValueError("Деление на ноль невозможно")
    return a / b

class Calculator:
    """Класс калькулятора с методами для математических операций"""
    
    def __init__(self, initial_value=0):
        self.value = initial_value
    
    def add(self, number):
        """Добавляет число к текущему значению"""
        self.value += number
        return self.value
    
    def subtract(self, number):
        """Вычитает число из текущего значения"""
        self.value -= number
        return self.value
    
    def multiply(self, number):
        """Умножает текущее значение на число"""
        self.value *= number
        return self.value
    
    def divide(self, number):
        """Делит текущее значение на число"""
        if number == 0:
            raise ValueError("Деление на ноль невозможно")
        self.value /= number
        return self.value
    
    def get_value(self):
        """Возвращает текущее значение"""
        return self.value
    
    def reset(self):
        """Сбрасывает значение к нулю"""
        self.value = 0
        return self.value

def main():
    """Основная функция для демонстрации"""
    print("Тестирование функций калькулятора:")
    print(f"add(5, 3) = {add(5, 3)}")
    print(f"subtract(10, 4) = {subtract(10, 4)}")
    print(f"multiply(6, 7) = {multiply(6, 7)}")
    print(f"divide(20, 5) = {divide(20, 5)}")
    
    print("\nТестирование класса Calculator:")
    calc = Calculator(10)
    print(f"Начальное значение: {calc.get_value()}")
    print(f"add(5): {calc.add(5)}")
    print(f"multiply(2): {calc.multiply(2)}")
    print(f"subtract(3): {calc.subtract(3)}")
    print(f"divide(4): {calc.divide(4)}")
    print(f"Финальное значение: {calc.get_value()}")

if __name__ == "__main__":
    main()
