#!/usr/bin/env python3
"""
Python Runner MCP Server
Запускает конкретные Python файлы и генерирует тесты для них
"""

import json
import subprocess
import logging
import ast
import tempfile
import os
import openai
from typing import Dict, Any, List
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PythonRunnerMCPServer:
    """MCP сервер для запуска Python файлов и генерации тестов"""
    
    def __init__(self):
        # Загружаем переменные окружения
        load_dotenv('docker.env')
        
        # Инициализируем OpenAI клиент
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            raise ValueError("OPENAI_API_KEY не настроен в docker.env файле!")
        
        openai.api_key = api_key
        logger.info("OpenAI API настроен успешно")
        self.tools = [
            {
                "name": "run-python-file",
                "description": "Запускает конкретный Python файл",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Путь к Python файлу для запуска"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "test-python-code",
                "description": "Генерирует и запускает полноценные тесты для Python файла",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Путь к Python файлу для тестирования (относительно /host директории)"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        ]
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Возвращает список доступных инструментов"""
        return self.tools
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Вызывает указанный инструмент"""
        if name == "run-python-file":
            return self.run_python_file(arguments)
        elif name == "test-python-code":
            return self.test_python_code(arguments)
        else:
            raise ValueError(f"Неизвестный инструмент: {name}")
    
    def run_python_file(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Запускает Python файл"""
        file_path = arguments.get("file_path")
        
        if not file_path:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Ошибка: не указан путь к файлу"
                    }
                ]
            }
        
        try:
            logger.info(f"Запуск Python файла: {file_path}")
            
            # Запускаем Python файл
            result = subprocess.run(
                ["python3", file_path],
                capture_output=True,
                text=True,
                timeout=30  # Таймаут 30 секунд
            )
            
            # Формируем результат
            if result.returncode == 0:
                output = result.stdout.strip()
                logger.info(f"Файл {file_path} выполнен успешно")
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"✅ Файл {file_path} выполнен успешно!\n\n**Вывод:**\n```\n{output}\n```"
                        }
                    ]
                }
            else:
                error_output = result.stderr.strip()
                logger.error(f"Ошибка выполнения файла {file_path}: {error_output}")
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Ошибка выполнения файла {file_path}!\n\n**Код ошибки:** {result.returncode}\n\n**Ошибка:**\n```\n{error_output}\n```"
                        }
                    ]
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"Таймаут выполнения файла {file_path}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"⏰ Таймаут выполнения файла {file_path} (30 секунд)"
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Ошибка запуска файла {file_path}: {str(e)}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"💥 Ошибка запуска файла {file_path}: {str(e)}"
                    }
                ]
            }
    
    def test_python_code(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Генерирует и запускает тесты для Python файла"""
        file_path = arguments.get("file_path")
        
        if not file_path:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Ошибка: не указан путь к файлу"
                    }
                ]
            }
        
        try:
            logger.info(f"Начинаю тестирование Python файла: {file_path}")
            
            # Проверяем существование файла
            if not os.path.exists(file_path):
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Файл {file_path} не найден!"
                        }
                    ]
                }
            
            # Читаем содержимое файла
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            logger.info(f"Файл {file_path} прочитан, размер: {len(source_code)} символов")
            
            # Анализируем код и генерируем тесты
            test_code = self._generate_tests(source_code, file_path)
            
            if not test_code:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Не удалось сгенерировать тесты для файла {file_path}. Возможно, файл не содержит функций или классов для тестирования."
                        }
                    ]
                }
            
            # Создаем временную директорию
            with tempfile.TemporaryDirectory() as temp_dir:
                # Копируем оригинальный файл во временную директорию
                original_filename = os.path.basename(file_path)
                temp_original_file = os.path.join(temp_dir, original_filename)
                
                with open(file_path, 'r', encoding='utf-8') as src, open(temp_original_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                
                # Создаем файл с тестами в той же директории
                test_filename = f"test_{original_filename}"
                temp_test_file = os.path.join(temp_dir, test_filename)
                
                with open(temp_test_file, 'w', encoding='utf-8') as test_file:
                    test_file.write(test_code)
                
                logger.info(f"Временная директория создана: {temp_dir}")
                logger.info(f"Оригинальный файл скопирован: {temp_original_file}")
                logger.info(f"Файл с тестами создан: {temp_test_file}")
                
                # Запускаем тесты
                test_result = self._run_tests(temp_test_file, temp_original_file)
            
            return test_result
            
        except Exception as e:
            logger.error(f"Ошибка тестирования файла {file_path}: {str(e)}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"💥 Ошибка тестирования файла {file_path}: {str(e)}"
                    }
                ]
            }
    
    def _generate_tests(self, source_code: str, file_path: str) -> str:
        """Генерирует тесты для Python кода используя OpenAI"""
        return self._generate_tests_with_openai(source_code, file_path)
    
    def _generate_tests_with_openai(self, source_code: str, file_path: str) -> str:
        """Генерирует тесты используя OpenAI API"""
        try:
            logger.info(f"Генерирую тесты для {file_path} используя OpenAI API")
            
            # Формируем промпт для OpenAI
            prompt = f"""Сгенерируй полноценные Python тесты для следующего кода. 

Файл: {file_path}

Код:
```python
{source_code}
```

Требования к тестам:
1. Используй pytest
2. Покрой все функции и классы
3. Включи позитивные и негативные тесты
4. Добавь тесты граничных случаев
5. Используй assert для проверок
6. Добавь docstring для каждого теста
7. Обработай возможные исключения
8. Сделай тесты читаемыми и понятными
9. ВАЖНО: Используй переменную `test_module` для доступа к функциям и классам
10. Например: `test_module.add(1, 2)` или `test_module.Calculator()`
11. НЕ используй прямые вызовы функций - всегда используй `test_module.`
12. Убедись что все тесты используют `test_module.` для доступа к функциям

Сгенерируй только код тестов без дополнительных комментариев или объяснений."""

            # Вызываем OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты эксперт по Python тестированию. Генерируй качественные тесты с использованием pytest."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.3
            )
            
            # Извлекаем сгенерированный код
            test_code = response.choices[0].message.content.strip()
            
            logger.info(f"OpenAI сгенерировал тесты: {test_code[:200]}...")
            
            # Добавляем необходимые импорты и настройки
            full_test_code = f"""#!/usr/bin/env python3
\"\"\"
Автоматически сгенерированные тесты для файла: {file_path}
Сгенерировано OpenAI API
\"\"\"

import sys
import os
import pytest

# Добавляем путь к директории с тестируемым файлом
sys.path.insert(0, os.path.dirname(os.path.abspath('{file_path}')))

# Импортируем модуль для тестирования
try:
    module_name = os.path.splitext(os.path.basename('{file_path}'))[0]
    test_module = __import__(module_name)
except ImportError as e:
    print(f"Ошибка импорта модуля {{module_name}}: {{e}}")
    print(f"Путь к модулю: {{os.path.abspath('{file_path}')}}")
    print(f"Директория модуля: {{os.path.dirname(os.path.abspath('{file_path}'))}}")
    print(f"sys.path: {{sys.path}}")
    sys.exit(1)

{test_code}

if __name__ == "__main__":
    # Запускаем тесты
    pytest.main([__file__, "-v"])
"""
            
            logger.info(f"OpenAI API успешно сгенерировал тесты для {file_path}")
            return full_test_code
            
        except Exception as e:
            logger.error(f"Ошибка OpenAI API при генерации тестов: {e}")
            raise e
    
    def _run_tests(self, test_file: str, original_file: str) -> Dict[str, Any]:
        """Fallback алгоритм генерации тестов (старая реализация)"""
        try:
            logger.info(f"Использую fallback алгоритм для генерации тестов: {file_path}")
            
            # Парсим код
            tree = ast.parse(source_code)
            
            # Собираем детальную информацию о коде
            module_functions = []  # Функции на уровне модуля
            classes = []  # Классы с их методами
            imports = []  # Импорты для анализа зависимостей
            
            # Анализируем узлы верхнего уровня
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    # Функция на уровне модуля
                    func_info = self._analyze_function(node)
                    module_functions.append(func_info)
                elif isinstance(node, ast.ClassDef):
                    # Класс с методами
                    class_info = self._analyze_class(node)
                    classes.append(class_info)
                elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    # Импорты
                    imports.append(node)
            
            if not module_functions and not classes:
                logger.warning(f"В файле {file_path} не найдено функций или классов для тестирования")
                return ""
            
            # Генерируем тесты
            test_code = f"""#!/usr/bin/env python3
\"\"\"
Автоматически сгенерированные тесты для файла: {file_path}
Покрытие: функции модуля, классы, методы, граничные случаи
\"\"\"

import sys
import os
import pytest
import inspect

# Добавляем путь к директории с тестируемым файлом
sys.path.insert(0, os.path.dirname(os.path.abspath('{file_path}')))

# Импортируем модуль для тестирования
try:
    # Используем абсолютный путь для импорта
    module_path = os.path.abspath('{file_path}')
    module_dir = os.path.dirname(module_path)
    module_name = os.path.splitext(os.path.basename(module_path))[0]
    
    # Добавляем директорию модуля в путь
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
    
    test_module = __import__(module_name)
except ImportError as e:
    print(f"Ошибка импорта модуля {{module_name}}: {{e}}")
    print(f"Путь к модулю: {{module_path}}")
    print(f"Директория модуля: {{module_dir}}")
    print(f"sys.path: {{sys.path}}")
    sys.exit(1)

# Вспомогательные функции для генерации тестовых данных
def generate_test_value_for_arg(arg_name):
    \"\"\"Генерирует тестовое значение для аргумента на основе имени\"\"\"
    arg_lower = arg_name.lower()
    
    if 'number' in arg_lower or 'num' in arg_lower or 'value' in arg_lower:
        return 42
    elif 'string' in arg_lower or 'text' in arg_lower or 'name' in arg_lower:
        return "test_string"
    elif 'list' in arg_lower or 'array' in arg_lower:
        return [1, 2, 3]
    elif 'dict' in arg_lower or 'map' in arg_lower:
        return {{"key": "value"}}
    elif 'bool' in arg_lower or 'flag' in arg_lower:
        return True
    elif 'file' in arg_lower or 'path' in arg_lower:
        return "/tmp/test_file.txt"
    else:
        # По умолчанию используем число
        return 42

def generate_test_args_for_function(func_name, args, defaults):
    \"\"\"Генерирует тестовые аргументы для функции\"\"\"
    test_args = []
    
    for i, arg in enumerate(args):
        if i < len(defaults):
            # Есть значение по умолчанию
            try:
                test_args.append(eval(defaults[i]))
            except:
                test_args.append(generate_test_value_for_arg(arg))
        else:
            # Генерируем тестовое значение
            test_args.append(generate_test_value_for_arg(arg))
    
    return test_args

def generate_test_args_for_class(class_name, args):
    \"\"\"Генерирует тестовые аргументы для конструктора класса\"\"\"
    test_args = []
    
    for arg in args:
        test_args.append(generate_test_value_for_arg(arg))
    
    return test_args

def generate_test_args_for_method(class_name, method_name, args, defaults):
    \"\"\"Генерирует тестовые аргументы для метода класса\"\"\"
    test_args = []
    
    for i, arg in enumerate(args):
        if i < len(defaults):
            # Есть значение по умолчанию
            try:
                test_args.append(eval(defaults[i]))
            except:
                test_args.append(generate_test_value_for_arg(arg))
        else:
            # Генерируем тестовое значение
            test_args.append(generate_test_value_for_arg(arg))
    
    return test_args

"""
            
            # Добавляем тесты для функций модуля
            for func_info in module_functions:
                test_code += self._generate_function_tests(func_info)
            
            # Добавляем тесты для классов
            for class_info in classes:
                test_code += self._generate_class_tests(class_info)
            
            # Добавляем интеграционные тесты
            test_code += self._generate_integration_tests(module_functions, classes)
            
            # Добавляем общие тесты модуля
            test_code += f"""
def test_module_import():
    \"\"\"Тест импорта модуля\"\"\"
    try:
        assert test_module is not None
        print(f"✅ Модуль {{module_name}} успешно импортирован")
    except Exception as e:
        pytest.fail("Тест импорта модуля провален: " + str(e))

def test_module_structure():
    \"\"\"Тест структуры модуля\"\"\"
    # Проверяем что модуль содержит ожидаемые элементы
    expected_functions = {[f['name'] for f in module_functions]}
    expected_classes = {[c['name'] for c in classes]}
    
    for func_name in expected_functions:
        assert hasattr(test_module, func_name), f"Функция {{func_name}} не найдена в модуле"
        assert callable(getattr(test_module, func_name)), f"{{func_name}} не является вызываемой функцией"
    
    for class_name in expected_classes:
        assert hasattr(test_module, class_name), f"Класс {{class_name}} не найден в модуле"
        class_obj = getattr(test_module, class_name)
        assert isinstance(class_obj, type), f"{{class_name}} не является классом"

if __name__ == "__main__":
    # Запускаем тесты
    pytest.main([__file__, "-v"])
"""
            
            logger.info(f"Fallback алгоритм сгенерировал тесты для {len(module_functions)} функций модуля и {len(classes)} классов")
            return test_code
            
        except SyntaxError as e:
            logger.error(f"Ошибка синтаксиса в файле {file_path}: {e}")
            return ""
        except Exception as e:
            logger.error(f"Ошибка fallback генерации тестов для файла {file_path}: {e}")
            return ""
    
    def _analyze_function(self, func_node: ast.FunctionDef) -> dict:
        """Анализирует функцию и возвращает информацию для тестирования"""
        func_info = {
            'name': func_node.name,
            'args': [],
            'defaults': [],
            'docstring': ast.get_docstring(func_node),
            'has_return': False,
            'complexity': 0
        }
        
        # Анализируем аргументы
        for arg in func_node.args.args:
            func_info['args'].append(arg.arg)
        
        # Анализируем значения по умолчанию
        if func_node.args.defaults:
            func_info['defaults'] = [ast.unparse(default) for default in func_node.args.defaults]
        
        # Проверяем наличие return
        for node in ast.walk(func_node):
            if isinstance(node, ast.Return):
                func_info['has_return'] = True
                break
        
        # Простая оценка сложности
        func_info['complexity'] = len(list(ast.walk(func_node)))
        
        return func_info
    
    def _analyze_class(self, class_node: ast.ClassDef) -> dict:
        """Анализирует класс и возвращает информацию для тестирования"""
        class_info = {
            'name': class_node.name,
            'methods': [],
            'docstring': ast.get_docstring(class_node),
            'has_init': False,
            'init_args': []
        }
        
        # Анализируем методы класса
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                method_info = self._analyze_function(node)
                class_info['methods'].append(method_info)
                
                # Проверяем конструктор
                if node.name == '__init__':
                    class_info['has_init'] = True
                    class_info['init_args'] = method_info['args'][1:]  # Исключаем self
        
        return class_info
    
    def _generate_function_tests(self, func_info: dict) -> str:
        """Генерирует тесты для функции модуля"""
        func_name = func_info['name']
        args = func_info['args']
        defaults = func_info['defaults']
        has_return = func_info['has_return']
        
        test_code = f"""
def test_{func_name}_function():
    \"\"\"Тест функции {func_name}\"\"\"
    try:
        # Проверяем что функция существует
        assert hasattr(test_module, '{func_name}')
        
        # Проверяем что это функция
        func = getattr(test_module, '{func_name}')
        assert callable(func)
        
        # Проверяем сигнатуру функции
        sig = inspect.signature(func)
        assert len(sig.parameters) == {len(args)}, f"Функция {func_name} должна принимать {len(args)} параметров"
        
        print(f"✅ Функция {func_name} найдена и имеет правильную сигнатуру")
        
    except Exception as e:
        pytest.fail("Тест функции {func_name} провален: " + str(e))

def test_{func_name}_execution():
    \"\"\"Тест выполнения функции {func_name}\"\"\"
    try:
        func = getattr(test_module, '{func_name}')
        
        # Генерируем тестовые данные на основе аргументов
        test_args = generate_test_args_for_function('{func_name}', {args}, {defaults})
        
        # Выполняем функцию с тестовыми данными
        if test_args:
            result = func(*test_args)
            
            # Проверяем что функция выполнилась без ошибок
            if {has_return}:
                assert result is not None, f"Функция {func_name} должна возвращать результат"
            
            print(f"✅ Функция {func_name} выполнилась успешно с аргументами {{test_args}}")
        else:
            print(f"⚠️ Не удалось сгенерировать тестовые данные для функции {func_name}")
            
    except Exception as e:
        pytest.fail("Тест выполнения функции {func_name} провален: " + str(e))

def test_{func_name}_logic():
    \"\"\"Тест логики функции {func_name}\"\"\"
    try:
        func = getattr(test_module, '{func_name}')
        
        # Тестируем логику на основе имени функции
        if '{func_name}' == 'add':
            result = func(5, 3)
            assert result == 8, f"add(5, 3) должен возвращать 8, а не {{result}}"
            print(f"✅ Логика функции {func_name}: add(5, 3) = {{result}}")
            
        elif '{func_name}' == 'subtract':
            result = func(10, 4)
            assert result == 6, f"subtract(10, 4) должен возвращать 6, а не {{result}}"
            print(f"✅ Логика функции {func_name}: subtract(10, 4) = {{result}}")
            
        elif '{func_name}' == 'multiply':
            result = func(6, 7)
            assert result == 42, f"multiply(6, 7) должен возвращать 42, а не {{result}}"
            print(f"✅ Логика функции {func_name}: multiply(6, 7) = {{result}}")
            
        elif '{func_name}' == 'divide':
            result = func(20, 5)
            assert result == 4, f"divide(20, 5) должен возвращать 4, а не {{result}}"
            print(f"✅ Логика функции {func_name}: divide(20, 5) = {{result}}")
            
        elif '{func_name}' == 'main':
            # Для main функции проверяем что она выполняется без ошибок
            result = func()
            print(f"✅ Функция {func_name} выполнилась успешно")
            
        else:
            # Для других функций проверяем базовую логику
            test_args = generate_test_args_for_function('{func_name}', {args}, {defaults})
            if test_args:
                result = func(*test_args)
                print(f"✅ Функция {func_name} выполнилась с результатом: {{result}}")
            else:
                print(f"⚠️ Не удалось протестировать логику функции {func_name}")
                
    except Exception as e:
        pytest.fail("Тест логики функции {func_name} провален: " + str(e))

"""
        
        return test_code
    
    def _generate_class_tests(self, class_info: dict) -> str:
        """Генерирует тесты для класса"""
        class_name = class_info['name']
        methods = class_info['methods']
        has_init = class_info['has_init']
        init_args = class_info['init_args']
        
        test_code = f"""
def test_{class_name}_class():
    \"\"\"Тест класса {class_name}\"\"\"
    try:
        # Проверяем что класс существует
        assert hasattr(test_module, '{class_name}')
        
        # Проверяем что это класс
        class_obj = getattr(test_module, '{class_name}')
        assert isinstance(class_obj, type)
        
        print(f"✅ Класс {class_name} найден и является классом")
        
    except Exception as e:
        pytest.fail("Тест класса {class_name} провален: " + str(e))

def test_{class_name}_instantiation():
    \"\"\"Тест создания экземпляра класса {class_name}\"\"\"
    try:
        class_obj = getattr(test_module, '{class_name}')
        
        # Создаем экземпляр с разными параметрами
        if {has_init}:
            # С конструктором
            if {init_args}:
                # С аргументами
                test_args = generate_test_args_for_class('{class_name}', {init_args})
                if test_args:
                    instance = class_obj(*test_args)
                    assert isinstance(instance, class_obj)
                    print(f"✅ Экземпляр {class_name} создан с аргументами {{test_args}}")
                else:
                    # Без аргументов (используем значения по умолчанию)
                    instance = class_obj()
                    assert isinstance(instance, class_obj)
                    print(f"✅ Экземпляр {class_name} создан без аргументов")
            else:
                # Конструктор без аргументов
                instance = class_obj()
                assert isinstance(instance, class_obj)
                print(f"✅ Экземпляр {class_name} создан")
        else:
            # Без конструктора
            instance = class_obj()
            assert isinstance(instance, class_obj)
            print(f"✅ Экземпляр {class_name} создан")
            
    except Exception as e:
        pytest.fail("Тест создания экземпляра класса {class_name} провален: " + str(e))

"""
        
        # Добавляем тесты для каждого метода
        for method_info in methods:
            if method_info['name'] != '__init__':
                test_code += self._generate_method_tests(class_name, method_info)
        
        return test_code
    
    def _generate_method_tests(self, class_name: str, method_info: dict) -> str:
        """Генерирует тесты для метода класса"""
        method_name = method_info['name']
        args = method_info['args'][1:]  # Исключаем self
        defaults = method_info['defaults']
        has_return = method_info['has_return']
        
        test_code = f"""
def test_{class_name}_{method_name}_method():
    \"\"\"Тест метода {method_name} класса {class_name}\"\"\"
    try:
        class_obj = getattr(test_module, '{class_name}')
        
        # Создаем экземпляр для тестирования
        if {len(args)} > 0 and {len(defaults)} == 0:
            # Метод требует аргументы, создаем с минимальными параметрами
            test_init_args = generate_test_args_for_class('{class_name}', [])
            if test_init_args:
                instance = class_obj(*test_init_args)
            else:
                instance = class_obj()
        else:
            instance = class_obj()
        
        # Получаем метод
        method = getattr(instance, '{method_name}')
        assert callable(method)
        
        # Генерируем тестовые данные для метода
        test_args = generate_test_args_for_method('{class_name}', '{method_name}', {args}, {defaults})
        
        # Выполняем метод
        if test_args:
            result = method(*test_args)
            
            # Проверяем результат
            if {has_return}:
                assert result is not None, f"Метод {method_name} должен возвращать результат"
            
            print(f"✅ Метод {method_name} класса {class_name} выполнился с аргументами {{test_args}}")
        else:
            print(f"⚠️ Не удалось сгенерировать тестовые данные для метода {method_name}")
            
    except Exception as e:
        pytest.fail("Тест метода {method_name} класса {class_name} провален: " + str(e))

def test_{class_name}_{method_name}_logic():
    \"\"\"Тест логики метода {method_name} класса {class_name}\"\"\"
    try:
        class_obj = getattr(test_module, '{class_name}')
        
        # Создаем экземпляр для тестирования логики
        if '{class_name}' == 'Calculator':
            instance = class_obj(10)  # Начальное значение 10
            
            if '{method_name}' == 'add':
                result = instance.add(5)
                assert result == 15, f"Calculator(10).add(5) должен возвращать 15, а не {{result}}"
                print(f"✅ Логика метода {method_name}: Calculator(10).add(5) = {{result}}")
                
            elif '{method_name}' == 'subtract':
                result = instance.subtract(3)
                assert result == 7, f"Calculator(10).subtract(3) должен возвращать 7, а не {{result}}"
                print(f"✅ Логика метода {method_name}: Calculator(10).subtract(3) = {{result}}")
                
            elif '{method_name}' == 'multiply':
                result = instance.multiply(2)
                assert result == 20, f"Calculator(10).multiply(2) должен возвращать 20, а не {{result}}"
                print(f"✅ Логика метода {method_name}: Calculator(10).multiply(2) = {{result}}")
                
            elif '{method_name}' == 'divide':
                result = instance.divide(2)
                assert result == 5, f"Calculator(10).divide(2) должен возвращать 5, а не {{result}}"
                print(f"✅ Логика метода {method_name}: Calculator(10).divide(2) = {{result}}")
                
            elif '{method_name}' == 'get_value':
                result = instance.get_value()
                assert result == 10, f"Calculator(10).get_value() должен возвращать 10, а не {{result}}"
                print(f"✅ Логика метода {method_name}: Calculator(10).get_value() = {{result}}")
                
            elif '{method_name}' == 'reset':
                result = instance.reset()
                assert result == 0, f"Calculator(10).reset() должен возвращать 0, а не {{result}}"
                print(f"✅ Логика метода {method_name}: Calculator(10).reset() = {{result}}")
                
            else:
                # Для других методов проверяем базовую логику
                test_args = generate_test_args_for_method('{class_name}', '{method_name}', {args}, {defaults})
                if test_args:
                    result = method(*test_args)
                    print(f"✅ Метод {method_name} выполнился с результатом: {{result}}")
                else:
                    print(f"⚠️ Не удалось протестировать логику метода {method_name}")
        else:
            # Для других классов проверяем базовую логику
            instance = class_obj()
            test_args = generate_test_args_for_method('{class_name}', '{method_name}', {args}, {defaults})
            if test_args:
                method = getattr(instance, '{method_name}')
                result = method(*test_args)
                print(f"✅ Метод {method_name} класса {class_name} выполнился с результатом: {{result}}")
            else:
                print(f"⚠️ Не удалось протестировать логику метода {method_name}")
                
    except Exception as e:
        pytest.fail("Тест логики метода {method_name} класса {class_name} провален: " + str(e))

"""
        
        return test_code
    
    def _generate_integration_tests(self, module_functions: list, classes: list) -> str:
        """Генерирует интеграционные тесты"""
        test_code = """
def test_integration_basic_flow():
    \"\"\"Интеграционный тест базового потока работы\"\"\"
    try:
        # Проверяем что модуль загружается корректно
        assert test_module is not None
        
        # Проверяем что все ожидаемые элементы доступны
        expected_functions = """ + str([f['name'] for f in module_functions]) + """
        expected_classes = """ + str([c['name'] for c in classes]) + """
        
        for func_name in expected_functions:
            assert hasattr(test_module, func_name), f"Функция {func_name} не найдена"
        
        for class_name in expected_classes:
            assert hasattr(test_module, class_name), f"Класс {class_name} не найден"
        
        print("✅ Интеграционный тест пройден - все элементы модуля доступны")
        
    except Exception as e:
        pytest.fail("Интеграционный тест провален: " + str(e))

"""
        
        return test_code
    
    def _generate_test_args_for_function(self, func_name: str, args: list, defaults: list) -> list:
        """Генерирует тестовые аргументы для функции"""
        # Простая генерация тестовых данных
        test_args = []
        
        for i, arg in enumerate(args):
            if i < len(defaults):
                # Есть значение по умолчанию
                test_args.append(eval(defaults[i]))
            else:
                # Генерируем тестовое значение
                test_args.append(self._generate_test_value_for_arg(arg))
        
        return test_args
    
    def _generate_test_args_for_class(self, class_name: str, args: list) -> list:
        """Генерирует тестовые аргументы для конструктора класса"""
        test_args = []
        
        for arg in args:
            test_args.append(self._generate_test_value_for_arg(arg))
        
        return test_args
    
    def _generate_test_args_for_method(self, class_name: str, method_name: str, args: list, defaults: list) -> list:
        """Генерирует тестовые аргументы для метода класса"""
        test_args = []
        
        for i, arg in enumerate(args):
            if i < len(defaults):
                # Есть значение по умолчанию
                test_args.append(eval(defaults[i]))
            else:
                # Генерируем тестовое значение
                test_args.append(self._generate_test_value_for_arg(arg))
        
        return test_args
    
    def _generate_test_value_for_arg(self, arg_name: str) -> any:
        """Генерирует тестовое значение для аргумента на основе имени"""
        # Простая эвристика для генерации тестовых данных
        arg_lower = arg_name.lower()
        
        if 'number' in arg_lower or 'num' in arg_lower or 'value' in arg_lower:
            return 42
        elif 'string' in arg_lower or 'text' in arg_lower or 'name' in arg_lower:
            return "test_string"
        elif 'list' in arg_lower or 'array' in arg_lower:
            return [1, 2, 3]
        elif 'dict' in arg_lower or 'map' in arg_lower:
            return {"key": "value"}
        elif 'bool' in arg_lower or 'flag' in arg_lower:
            return True
        elif 'file' in arg_lower or 'path' in arg_lower:
            return "/tmp/test_file.txt"
        else:
            # По умолчанию используем число
            return 42
    
    def _run_tests(self, test_file: str, original_file: str) -> Dict[str, Any]:
        """Запускает тесты и возвращает результаты"""
        try:
            logger.info(f"Запуск тестов из файла: {test_file}")
            logger.info(f"Оригинальный файл: {original_file}")
            
            # Сначала читаем содержимое тестового файла для отладки
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    test_content = f.read()
                logger.info(f"Содержимое тестового файла (первые 500 символов): {test_content[:500]}...")
            except Exception as e:
                logger.error(f"Не удалось прочитать тестовый файл: {e}")
            
            # Запускаем pytest из временной директории
            test_dir = os.path.dirname(test_file)
            
            # Запускаем pytest из директории с тестами
            result = subprocess.run(
                ["python3", "-m", "pytest", test_file, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60,  # Таймаут 60 секунд для тестов
                cwd=test_dir  # Рабочая директория - временная директория с файлами
            )
            
            # Анализируем результаты
            if result.returncode == 0:
                # Тесты прошли успешно
                output = result.stdout.strip()
                logger.info(f"Тесты для файла {original_file} прошли успешно")
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"✅ **Тесты для файла {original_file} прошли успешно!**\n\n**Результаты тестирования:**\n```\n{output}\n```\n\n🎉 Все тесты пройдены! Код работает корректно."
                        }
                    ]
                }
            else:
                # Тесты провалились
                error_output = result.stderr.strip()
                stdout_output = result.stdout.strip()
                
                logger.warning(f"Тесты для файла {original_file} провалились")
                
                # Формируем детальный отчет
                report = f"❌ **Тесты для файла {original_file} провалились!**\n\n"
                report += f"**Код возврата:** {result.returncode}\n\n"
                
                if stdout_output:
                    report += f"**Вывод тестов:**\n```\n{stdout_output}\n```\n\n"
                
                if error_output:
                    report += f"**Ошибки тестирования:**\n```\n{error_output}\n```\n\n"
                
                report += "🔍 **Рекомендации:**\n"
                report += "- Проверьте синтаксис Python кода\n"
                report += "- Убедитесь что все импорты корректны\n"
                report += "- Проверьте что функции и классы определены правильно\n"
                report += "- Проверьте логику функций и методов\n"
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": report
                        }
                    ]
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"Таймаут выполнения тестов для файла {original_file}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"⏰ **Таймаут выполнения тестов** для файла {original_file} (60 секунд)\n\nВозможно, тесты выполняются слишком долго или есть бесконечные циклы."
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Ошибка запуска тестов для файла {original_file}: {str(e)}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"💥 **Ошибка запуска тестов** для файла {original_file}: {str(e)}\n\nПроверьте что pytest установлен и доступен в системе."
                    }
                ]
            }
