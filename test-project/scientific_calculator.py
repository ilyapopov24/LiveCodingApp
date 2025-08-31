#!/usr/bin/env python3
"""
Научный калькулятор с расширенными математическими функциями
Демонстрирует сложную логику для тестирования тулсы test-python-code
"""

import math
import cmath
from typing import Union, List, Tuple, Optional
from decimal import Decimal, getcontext

# Устанавливаем точность для Decimal
getcontext().prec = 28

class ScientificCalculator:
    """Класс научного калькулятора с расширенными функциями"""
    
    def __init__(self):
        self.history: List[str] = []
        self.memory: float = 0.0
        self.angle_mode: str = "degrees"  # radians или degrees (по умолчанию градусы для удобства)
        
    def add_to_history(self, operation: str, result: Union[int, float, str]) -> None:
        """Добавляет операцию в историю"""
        self.history.append(f"{operation} = {result}")
        if len(self.history) > 100:  # Ограничиваем историю
            self.history.pop(0)
    
    def clear_history(self) -> None:
        """Очищает историю операций"""
        self.history.clear()
    
    def get_history(self) -> List[str]:
        """Возвращает историю операций"""
        return self.history.copy()
    
    def set_memory(self, value: float) -> None:
        """Устанавливает значение в память"""
        self.memory = value
    
    def get_memory(self) -> float:
        """Возвращает значение из памяти"""
        return self.memory
    
    def clear_memory(self) -> None:
        """Очищает память"""
        self.memory = 0.0
    
    def set_angle_mode(self, mode: str) -> None:
        """Устанавливает режим углов (radians/degrees)"""
        if mode.lower() in ["radians", "degrees"]:
            self.angle_mode = mode.lower()
        else:
            raise ValueError("Режим углов должен быть 'radians' или 'degrees'")
    
    def to_radians(self, angle: float) -> float:
        """Конвертирует угол в радианы если нужно"""
        if self.angle_mode == "degrees":
            return math.radians(angle)
        return angle
    
    def to_degrees(self, angle: float) -> float:
        """Конвертирует угол в градусы если нужно"""
        if self.angle_mode == "radians":
            return math.degrees(angle)
        return angle
    
    def sin_deg(self, angle_degrees: float) -> float:
        """Синус угла в градусах (удобный метод для тестов)"""
        return math.sin(math.radians(angle_degrees))
    
    def cos_deg(self, angle_degrees: float) -> float:
        """Косинус угла в градусах (удобный метод для тестов)"""
        return math.cos(math.radians(angle_degrees))
    
    def tan_deg(self, angle_degrees: float) -> float:
        """Тангенс угла в градусах (удобный метод для тестов)"""
        return math.tan(math.radians(angle_degrees))

class BasicOperations:
    """Базовые математические операции"""
    
    @staticmethod
    def add(a: Union[int, float, Decimal], b: Union[int, float, Decimal]) -> Union[int, float, Decimal]:
        """Сложение двух чисел"""
        if isinstance(a, Decimal) or isinstance(b, Decimal):
            return Decimal(str(a)) + Decimal(str(b))
        return a + b
    
    @staticmethod
    def subtract(a: Union[int, float, Decimal], b: Union[int, float, Decimal]) -> Union[int, float, Decimal]:
        """Вычитание двух чисел"""
        if isinstance(a, Decimal) or isinstance(b, Decimal):
            return Decimal(str(a)) - Decimal(str(b))
        return a - b
    
    @staticmethod
    def multiply(a: Union[int, float, Decimal], b: Union[int, float, Decimal]) -> Union[int, float, Decimal]:
        """Умножение двух чисел"""
        if isinstance(a, Decimal) or isinstance(b, Decimal):
            return Decimal(str(a)) * Decimal(str(b))
        return a * b
    
    @staticmethod
    def divide(a: Union[int, float, Decimal], b: Union[int, float, Decimal]) -> Union[int, float, Decimal]:
        """Деление двух чисел"""
        if b == 0:
            raise ValueError("Деление на ноль невозможно")
        if isinstance(a, Decimal) or isinstance(b, Decimal):
            return Decimal(str(a)) / Decimal(str(b))
        return a / b
    
    @staticmethod
    def power(base: Union[int, float, Decimal], exponent: Union[int, float, Decimal]) -> Union[int, float, Decimal]:
        """Возведение в степень"""
        if isinstance(base, Decimal) or isinstance(exponent, Decimal):
            return Decimal(str(base)) ** Decimal(str(exponent))
        return base ** exponent
    
    @staticmethod
    def root(base: Union[int, float, Decimal], n: Union[int, float, Decimal]) -> Union[int, float, Decimal]:
        """Извлечение корня n-й степени"""
        if n == 0:
            raise ValueError("Степень корня не может быть нулем")
        if base < 0 and n % 2 == 0:
            raise ValueError("Четный корень из отрицательного числа не определен")
        if isinstance(base, Decimal) or isinstance(n, Decimal):
            return Decimal(str(base)) ** (Decimal('1') / Decimal(str(n)))
        return base ** (1 / n)

class TrigonometricFunctions:
    """Тригонометрические функции"""
    
    def __init__(self, calculator: ScientificCalculator):
        self.calc = calculator
    
    def sin(self, angle: float) -> float:
        """Синус угла"""
        rad_angle = self.calc.to_radians(angle)
        result = math.sin(rad_angle)
        self.calc.add_to_history(f"sin({angle})", result)
        return result
    
    def cos(self, angle: float) -> float:
        """Косинус угла"""
        rad_angle = self.calc.to_radians(angle)
        result = math.cos(rad_angle)
        self.calc.add_to_history(f"cos({angle})", result)
        return result
    
    def tan(self, angle: float) -> float:
        """Тангенс угла"""
        rad_angle = self.calc.to_radians(angle)
        result = math.tan(rad_angle)
        self.calc.add_to_history(f"tan({angle})", result)
        return result
    
    def asin(self, value: float) -> float:
        """Арксинус"""
        if not -1 <= value <= 1:
            raise ValueError("Арксинус определен только для значений от -1 до 1")
        result = math.asin(value)
        result = self.calc.to_degrees(result) if self.calc.angle_mode == "degrees" else result
        self.calc.add_to_history(f"asin({value})", result)
        return result
    
    def acos(self, value: float) -> float:
        """Арккосинус"""
        if not -1 <= value <= 1:
            raise ValueError("Арккосинус определен только для значений от -1 до 1")
        result = math.acos(value)
        result = self.calc.to_degrees(result) if self.calc.angle_mode == "degrees" else result
        self.calc.add_to_history(f"acos({value})", result)
        return result
    
    def atan(self, value: float) -> float:
        """Арктангенс"""
        result = math.atan(value)
        result = self.calc.to_degrees(result) if self.calc.angle_mode == "degrees" else result
        self.calc.add_to_history(f"atan({value})", result)
        return result

class AdvancedFunctions:
    """Продвинутые математические функции"""
    
    @staticmethod
    def factorial(n: int) -> int:
        """Факториал числа"""
        if n < 0:
            raise ValueError("Факториал не определен для отрицательных чисел")
        if n == 0 or n == 1:
            return 1
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
    
    @staticmethod
    def fibonacci(n: int) -> int:
        """Число Фибоначчи"""
        if n < 0:
            raise ValueError("Число Фибоначчи не определено для отрицательных индексов")
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    
    @staticmethod
    def is_prime(n: int) -> bool:
        """Проверка числа на простоту"""
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
    
    @staticmethod
    def gcd(a: int, b: int) -> int:
        """Наибольший общий делитель (алгоритм Евклида)"""
        while b:
            a, b = b, a % b
        return abs(a)
    
    @staticmethod
    def lcm(a: int, b: int) -> int:
        """Наименьшее общее кратное"""
        return abs(a * b) // AdvancedFunctions.gcd(a, b)
    
    @staticmethod
    def prime_factors(n: int) -> List[int]:
        """Разложение числа на простые множители"""
        if n < 2:
            return []
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return factors

class Statistics:
    """Статистические функции"""
    
    @staticmethod
    def mean(numbers: List[float]) -> float:
        """Среднее арифметическое"""
        if not numbers:
            raise ValueError("Список чисел не может быть пустым")
        return sum(numbers) / len(numbers)
    
    @staticmethod
    def median(numbers: List[float]) -> float:
        """Медиана"""
        if not numbers:
            raise ValueError("Список чисел не может быть пустым")
        sorted_numbers = sorted(numbers)
        n = len(sorted_numbers)
        if n % 2 == 0:
            return (sorted_numbers[n//2 - 1] + sorted_numbers[n//2]) / 2
        else:
            return sorted_numbers[n//2]
    
    @staticmethod
    def mode(numbers: List[float]) -> List[float]:
        """Мода (наиболее часто встречающиеся значения)"""
        if not numbers:
            raise ValueError("Список чисел не может быть пустым")
        frequency = {}
        for num in numbers:
            frequency[num] = frequency.get(num, 0) + 1
        
        max_freq = max(frequency.values())
        return [num for num, freq in frequency.items() if freq == max_freq]
    
    @staticmethod
    def variance(numbers: List[float]) -> float:
        """Дисперсия"""
        if len(numbers) < 2:
            raise ValueError("Для вычисления дисперсии нужно минимум 2 числа")
        mean_val = Statistics.mean(numbers)
        return sum((x - mean_val) ** 2 for x in numbers) / (len(numbers) - 1)
    
    @staticmethod
    def standard_deviation(numbers: List[float]) -> float:
        """Стандартное отклонение"""
        return math.sqrt(Statistics.variance(numbers))

class ComplexMath:
    """Работа с комплексными числами"""
    
    @staticmethod
    def complex_power(base: complex, exponent: complex) -> complex:
        """Возведение комплексного числа в комплексную степень"""
        return base ** exponent
    
    @staticmethod
    def complex_root(base: complex, n: int) -> List[complex]:
        """Все корни n-й степени комплексного числа"""
        if n <= 0:
            raise ValueError("Степень корня должна быть положительной")
        
        r = abs(base)
        theta = cmath.phase(base)
        
        roots = []
        for k in range(n):
            root_r = r ** (1/n)
            root_theta = (theta + 2 * math.pi * k) / n
            root = root_r * cmath.rect(1, root_theta)
            roots.append(root)
        
        return roots
    
    @staticmethod
    def complex_log(base: complex) -> complex:
        """Натуральный логарифм комплексного числа"""
        return cmath.log(base)
    
    @staticmethod
    def complex_power_simple(base: complex, exponent: int) -> complex:
        """Возведение комплексного числа в целую степень (упрощенная версия)"""
        return base ** exponent

def main():
    """Демонстрация работы научного калькулятора"""
    print("🧮 Научный калькулятор - Демонстрация функций")
    print("=" * 60)
    
    # Создаем экземпляр калькулятора
    calc = ScientificCalculator()
    trig = TrigonometricFunctions(calc)
    basic = BasicOperations()
    advanced = AdvancedFunctions()
    stats = Statistics()
    
    try:
        # Базовые операции
        print("📊 Базовые операции:")
        print(f"5 + 3 = {basic.add(5, 3)}")
        print(f"10 - 4 = {basic.subtract(10, 4)}")
        print(f"6 × 7 = {basic.multiply(6, 7)}")
        print(f"15 ÷ 3 = {basic.divide(15, 3)}")
        print(f"2^8 = {basic.power(2, 8)}")
        print(f"√16 = {basic.root(16, 2)}")
        
        # Тригонометрические функции
        print("\n📐 Тригонометрические функции (градусы):")
        calc.set_angle_mode("degrees")
        print(f"sin(30°) = {trig.sin(30):.6f}")
        print(f"cos(60°) = {trig.cos(60):.6f}")
        print(f"tan(45°) = {trig.tan(45):.6f}")
        
        # Продвинутые функции
        print("\n🔢 Продвинутые функции:")
        print(f"5! = {advanced.factorial(5)}")
        print(f"F(10) = {advanced.fibonacci(10)}")
        print(f"17 простое? {advanced.is_prime(17)}")
        print(f"НОД(48, 18) = {advanced.gcd(48, 18)}")
        print(f"НОК(12, 18) = {advanced.lcm(12, 18)}")
        print(f"Простые множители 84: {advanced.prime_factors(84)}")
        
        # Статистика
        print("\n📈 Статистические функции:")
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        print(f"Числа: {numbers}")
        print(f"Среднее: {stats.mean(numbers):.2f}")
        print(f"Медиана: {stats.median(numbers):.2f}")
        print(f"Мода: {stats.mode(numbers)}")
        print(f"Дисперсия: {stats.variance(numbers):.2f}")
        print(f"Стандартное отклонение: {stats.standard_deviation(numbers):.2f}")
        
        # Комплексные числа
        print("\n🔮 Комплексные числа:")
        z1 = complex(3, 4)
        z2 = complex(1, 2)
        print(f"z1 = {z1}")
        print(f"z2 = {z2}")
        print(f"z1 + z2 = {z1 + z2}")
        print(f"z1 × z2 = {z1 * z2}")
        print(f"z1^2 = {ComplexMath.complex_power(z1, 2)}")
        
        # История операций
        print("\n📚 История операций:")
        history = calc.get_history()
        for i, op in enumerate(history[-5:], 1):  # Последние 5 операций
            print(f"{i}. {op}")
        
        print("\n✅ Все функции работают корректно!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
