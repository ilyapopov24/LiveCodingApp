#!/usr/bin/env python3
"""
Научный калькулятор с расширенными математическими функциями
для тестирования возможностей нейронных сетей
"""

import math
import cmath
import statistics
from typing import Union, List, Tuple, Optional, Dict
from decimal import Decimal, getcontext

# Устанавливаем точность для десятичных вычислений
getcontext().prec = 28

class ScientificCalculator:
    """Научный калькулятор с расширенными математическими функциями"""
    
    def __init__(self, initial_value: Union[int, float, Decimal] = 0):
        self.value = Decimal(str(initial_value))
        self.history: List[Tuple[str, Union[int, float, Decimal]]] = []
        self.memory: Dict[str, Union[int, float, Decimal]] = {}
        self.angle_mode: str = "degrees"  # degrees или radians
        self.base_mode: int = 10  # 2, 8, 10, 16
    
    def add(self, number: Union[int, float, Decimal]) -> Decimal:
        """Сложение"""
        result = self.value + Decimal(str(number))
        self._add_to_history("add", number)
        self.value = result
        return result
    
    def subtract(self, number: Union[int, float, Decimal]) -> Decimal:
        """Вычитание"""
        result = self.value - Decimal(str(number))
        self._add_to_history("subtract", number)
        self.value = result
        return result
    
    def multiply(self, number: Union[int, float, Decimal]) -> Decimal:
        """Умножение"""
        result = self.value * Decimal(str(number))
        self._add_to_history("multiply", number)
        self.value = result
        return result
    
    def divide(self, number: Union[int, float, Decimal]) -> Decimal:
        """Деление"""
        if number == 0:
            raise ValueError("Деление на ноль невозможно")
        result = self.value / Decimal(str(number))
        self._add_to_history("divide", number)
        self.value = result
        return result
    
    def power(self, exponent: Union[int, float, Decimal]) -> Decimal:
        """Возведение в степень"""
        result = self.value ** Decimal(str(exponent))
        self._add_to_history("power", exponent)
        self.value = result
        return result
    
    def sqrt(self) -> Decimal:
        """Квадратный корень"""
        if self.value < 0:
            raise ValueError("Квадратный корень из отрицательного числа невозможен в действительных числах")
        result = self.value.sqrt()
        self._add_to_history("sqrt", None)
        self.value = result
        return result
    
    def cbrt(self) -> Decimal:
        """Кубический корень"""
        result = self.value ** (Decimal('1') / Decimal('3'))
        self._add_to_history("cbrt", None)
        self.value = result
        return result
    
    def factorial(self) -> int:
        """Факториал"""
        if not self.value.is_integer() or self.value < 0:
            raise ValueError("Факториал определен только для неотрицательных целых чисел")
        result = math.factorial(int(self.value))
        self._add_to_history("factorial", None)
        self.value = Decimal(str(result))
        return result
    
    def sin(self) -> float:
        """Синус"""
        angle = self._convert_angle(float(self.value))
        result = math.sin(angle)
        self._add_to_history("sin", None)
        self.value = Decimal(str(result))
        return result
    
    def cos(self) -> float:
        """Косинус"""
        angle = self._convert_angle(float(self.value))
        result = math.cos(angle)
        self._add_to_history("cos", None)
        self.value = Decimal(str(result))
        return result
    
    def tan(self) -> float:
        """Тангенс"""
        angle = self._convert_angle(float(self.value))
        result = math.tan(angle)
        self._add_to_history("tan", None)
        self.value = Decimal(str(result))
        return result
    
    def asin(self) -> float:
        """Арксинус"""
        if not -1 <= float(self.value) <= 1:
            raise ValueError("Арксинус определен только для значений от -1 до 1")
        result = math.asin(float(self.value))
        result = self._convert_angle_back(result)
        self._add_to_history("asin", None)
        self.value = Decimal(str(result))
        return result
    
    def acos(self) -> float:
        """Арккосинус"""
        if not -1 <= float(self.value) <= 1:
            raise ValueError("Арккосинус определен только для значений от -1 до 1")
        result = math.acos(float(self.value))
        result = self._convert_angle_back(result)
        self._add_to_history("acos", None)
        self.value = Decimal(str(result))
        return result
    
    def atan(self) -> float:
        """Арктангенс"""
        result = math.atan(float(self.value))
        result = self._convert_angle_back(result)
        self._add_to_history("atan", None)
        self.value = Decimal(str(result))
        return result
    
    def log(self, base: Union[int, float, Decimal] = 10) -> float:
        """Логарифм по заданному основанию"""
        if self.value <= 0:
            raise ValueError("Логарифм определен только для положительных чисел")
        if base <= 0 or base == 1:
            raise ValueError("Основание логарифма должно быть положительным и не равным 1")
        result = math.log(float(self.value), float(base))
        self._add_to_history("log", base)
        self.value = Decimal(str(result))
        return result
    
    def ln(self) -> float:
        """Натуральный логарифм"""
        if self.value <= 0:
            raise ValueError("Натуральный логарифм определен только для положительных чисел")
        result = math.log(float(self.value))
        self._add_to_history("ln", None)
        self.value = Decimal(str(result))
        return result
    
    def exp(self) -> float:
        """Экспонента (e^x)"""
        result = math.exp(float(self.value))
        self._add_to_history("exp", None)
        self.value = Decimal(str(result))
        return result
    
    def abs(self) -> Decimal:
        """Модуль числа"""
        result = abs(self.value)
        self._add_to_history("abs", None)
        self.value = result
        return result
    
    def floor(self) -> int:
        """Целая часть числа (округление вниз)"""
        result = math.floor(self.value)
        self._add_to_history("floor", None)
        self.value = Decimal(str(result))
        return result
    
    def ceil(self) -> int:
        """Целая часть числа (округление вверх)"""
        result = math.ceil(self.value)
        self._add_to_history("ceil", None)
        self.value = Decimal(str(result))
        return result
    
    def round_to(self, decimals: int = 0) -> Decimal:
        """Округление до заданного количества знаков после запятой"""
        result = round(self.value, decimals)
        self._add_to_history("round", decimals)
        self.value = Decimal(str(result))
        return result
    
    def mod(self, divisor: Union[int, float, Decimal]) -> Decimal:
        """Остаток от деления"""
        if divisor == 0:
            raise ValueError("Делитель не может быть равен нулю")
        result = self.value % Decimal(str(divisor))
        self._add_to_history("mod", divisor)
        self.value = result
        return result
    
    def gcd(self, other: Union[int, float, Decimal]) -> int:
        """Наибольший общий делитель"""
        result = math.gcd(int(self.value), int(Decimal(str(other))))
        self._add_to_history("gcd", other)
        self.value = Decimal(str(result))
        return result
    
    def lcm(self, other: Union[int, float, Decimal]) -> int:
        """Наименьшее общее кратное"""
        a, b = int(self.value), int(Decimal(str(other)))
        result = abs(a * b) // math.gcd(a, b)
        self._add_to_history("lcm", other)
        self.value = Decimal(str(result))
        return result
    
    def is_prime(self) -> bool:
        """Проверка на простоту числа"""
        if not self.value.is_integer() or self.value < 2:
            return False
        n = int(self.value)
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    def next_prime(self) -> int:
        """Следующее простое число"""
        if not self.value.is_integer():
            raise ValueError("Функция определена только для целых чисел")
        n = int(self.value) + 1
        while not self._is_prime(n):
            n += 1
        self._add_to_history("next_prime", None)
        self.value = Decimal(str(n))
        return n
    
    def prev_prime(self) -> int:
        """Предыдущее простое число"""
        if not self.value.is_integer():
            raise ValueError("Функция определена только для целых чисел")
        n = int(self.value) - 1
        if n < 2:
            raise ValueError("Предыдущего простого числа не существует")
        while not self._is_prime(n):
            n -= 1
        self._add_to_history("prev_prime", None)
        self.value = Decimal(str(n))
        return n
    
    def fibonacci(self) -> int:
        """n-ое число Фибоначчи"""
        if not self.value.is_integer() or self.value < 0:
            raise ValueError("Функция определена только для неотрицательных целых чисел")
        n = int(self.value)
        if n <= 1:
            result = n
        else:
            a, b = 0, 1
            for _ in range(2, n + 1):
                a, b = b, a + b
            result = b
        self._add_to_history("fibonacci", None)
        self.value = Decimal(str(result))
        return result
    
    def set_angle_mode(self, mode: str) -> None:
        """Установка режима углов (degrees/radians)"""
        if mode not in ["degrees", "radians"]:
            raise ValueError("Режим углов должен быть 'degrees' или 'radians'")
        self.angle_mode = mode
    
    def set_base_mode(self, base: int) -> None:
        """Установка системы счисления (2, 8, 10, 16)"""
        if base not in [2, 8, 10, 16]:
            raise ValueError("Основание должно быть 2, 8, 10 или 16")
        self.base_mode = base
    
    def convert_base(self, new_base: int) -> str:
        """Конвертация числа в другую систему счисления"""
        if new_base not in [2, 8, 10, 16]:
            raise ValueError("Основание должно быть 2, 8, 10 или 16")
        if not self.value.is_integer():
            raise ValueError("Конвертация возможна только для целых чисел")
        n = int(self.value)
        if new_base == 10:
            return str(n)
        elif new_base == 2:
            return bin(n)[2:]
        elif new_base == 8:
            return oct(n)[2:]
        elif new_base == 16:
            return hex(n)[2:].upper()
    
    def store_memory(self, key: str) -> None:
        """Сохранить значение в память"""
        self.memory[key] = float(self.value)
    
    def recall_memory(self, key: str) -> Optional[float]:
        """Восстановить значение из памяти"""
        return self.memory.get(key)
    
    def clear_memory(self, key: str = None) -> None:
        """Очистить память"""
        if key is None:
            self.memory.clear()
        else:
            self.memory.pop(key, None)
    
    def get_history(self) -> List[Tuple[str, Union[int, float, Decimal]]]:
        """Получить историю операций"""
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Очистить историю операций"""
        self.history.clear()
    
    def undo(self) -> Optional[Union[int, float, Decimal]]:
        """Отменить последнюю операцию"""
        if not self.history:
            return None
        operation, operand = self.history.pop()
        # Простая логика отмены - можно улучшить
        if operation == "add":
            self.value -= Decimal(str(operand))
        elif operation == "subtract":
            self.value += Decimal(str(operand))
        elif operation == "multiply":
            if operand != 0:
                self.value /= Decimal(str(operand))
        elif operation == "divide":
            if operand != 0:
                self.value *= Decimal(str(operand))
        return self.value
    
    def reset(self) -> Decimal:
        """Сброс значения к нулю"""
        self.value = Decimal('0')
        self._add_to_history("reset", None)
        return self.value
    
    def get_value(self) -> Decimal:
        """Получить текущее значение"""
        return self.value
    
    def set_value(self, value: Union[int, float, Decimal]) -> None:
        """Установить значение"""
        self.value = Decimal(str(value))
        self._add_to_history("set_value", value)
    
    def _add_to_history(self, operation: str, operand: Union[int, float, Decimal, None]) -> None:
        """Добавить операцию в историю"""
        self.history.append((operation, operand))
    
    def _convert_angle(self, angle: float) -> float:
        """Конвертировать угол в радианы если нужно"""
        if self.angle_mode == "degrees":
            return math.radians(angle)
        return angle
    
    def _convert_angle_back(self, angle: float) -> float:
        """Конвертировать угол обратно в градусы если нужно"""
        if self.angle_mode == "degrees":
            return math.degrees(angle)
        return angle
    
    def _is_prime(self, n: int) -> bool:
        """Вспомогательная функция для проверки простоты"""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True

# Утилитарные функции для работы с массивами
def calculate_statistics(numbers: List[Union[int, float]]) -> Dict[str, float]:
    """Вычислить статистические характеристики массива чисел"""
    if not numbers:
        raise ValueError("Массив не может быть пустым")
    
    return {
        "mean": statistics.mean(numbers),
        "median": statistics.median(numbers),
        "mode": statistics.mode(numbers) if len(numbers) > 1 else numbers[0],
        "variance": statistics.variance(numbers),
        "stdev": statistics.stdev(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "sum": sum(numbers),
        "count": len(numbers)
    }

def solve_quadratic(a: float, b: float, c: float) -> Tuple[complex, complex]:
    """Решить квадратное уравнение ax² + bx + c = 0"""
    if a == 0:
        raise ValueError("Коэффициент 'a' не может быть равен нулю")
    
    discriminant = b**2 - 4*a*c
    
    if discriminant >= 0:
        x1 = (-b + math.sqrt(discriminant)) / (2*a)
        x2 = (-b - math.sqrt(discriminant)) / (2*a)
    else:
        x1 = (-b + cmath.sqrt(discriminant)) / (2*a)
        x2 = (-b - cmath.sqrt(discriminant)) / (2*a)
    
    return x1, x2

def calculate_series_sum(series_type: str, n: int, **kwargs) -> float:
    """Вычислить сумму различных числовых рядов"""
    if n <= 0:
        raise ValueError("Количество членов должно быть положительным")
    
    if series_type == "arithmetic":
        a1 = kwargs.get('a1', 1)
        d = kwargs.get('d', 1)
        return n * (2*a1 + (n-1)*d) / 2
    
    elif series_type == "geometric":
        a1 = kwargs.get('a1', 1)
        r = kwargs.get('r', 2)
        if r == 1:
            return n * a1
        return a1 * (1 - r**n) / (1 - r)
    
    elif series_type == "harmonic":
        return sum(1/i for i in range(1, n+1))
    
    elif series_type == "fibonacci":
        if n <= 2:
            return n
        a, b, total = 1, 1, 2
        for _ in range(3, n+1):
            a, b = b, a + b
            total += b
        return total
    
    else:
        raise ValueError("Неизвестный тип ряда")

def main():
    """Демонстрация возможностей научного калькулятора"""
    print("🧮 Научный калькулятор - Демонстрация возможностей")
    print("=" * 60)
    
    # Создаем экземпляр калькулятора
    calc = ScientificCalculator(10)
    
    print(f"Начальное значение: {calc.get_value()}")
    
    # Базовые операции
    print(f"\n📊 Базовые операции:")
    print(f"add(5): {calc.add(5)}")
    print(f"multiply(3): {calc.multiply(3)}")
    print(f"power(2): {calc.power(2)}")
    print(f"sqrt(): {calc.sqrt()}")
    
    # Тригонометрические функции
    calc.set_value(45)
    print(f"\n📐 Тригонометрические функции (угол: {calc.get_value()}°):")
    print(f"sin(): {calc.sin():.6f}")
    print(f"cos(): {calc.cos():.6f}")
    print(f"tan(): {calc.tan():.6f}")
    
    # Логарифмы
    calc.set_value(100)
    print(f"\n📈 Логарифмы:")
    print(f"log(10): {calc.log(10):.6f}")
    print(f"ln(): {calc.ln():.6f}")
    
    # Проверка на простоту
    calc.set_value(17)
    print(f"\n🔢 Проверка на простоту:")
    print(f"Число {calc.get_value()} простое: {calc.is_prime()}")
    print(f"Следующее простое: {calc.next_prime()}")
    
    # Числа Фибоначчи
    calc.set_value(10)
    print(f"\n🐚 Числа Фибоначчи:")
    print(f"10-ое число Фибоначчи: {calc.fibonacci()}")
    
    # Статистика
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    print(f"\n📊 Статистика массива {numbers}:")
    stats = calculate_statistics(numbers)
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Квадратное уравнение
    print(f"\n🔍 Решение квадратного уравнения x² - 5x + 6 = 0:")
    x1, x2 = solve_quadratic(1, -5, 6)
    print(f"x₁ = {x1}, x₂ = {x2}")
    
    # Сумма ряда
    print(f"\n📈 Сумма арифметического ряда (10 членов, a₁=1, d=1):")
    series_sum = calculate_series_sum("arithmetic", 10, a1=1, d=1)
    print(f"Сумма: {series_sum}")
    
    print(f"\n🎉 Демонстрация завершена!")

if __name__ == "__main__":
    main()




