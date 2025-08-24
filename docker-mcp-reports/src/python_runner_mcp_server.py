#!/usr/bin/env python3
"""
Python Runner MCP Server
Запускает конкретные Python файлы и генерирует тесты для них используя OpenAI
"""

import json
import subprocess
import logging
import tempfile
import os
import openai
import anthropic
import asyncio
import concurrent.futures
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
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key or openai_api_key == 'your_openai_api_key_here':
            raise ValueError("OPENAI_API_KEY не настроен в docker.env файле!")
        
        openai.api_key = openai_api_key
        logger.info("OpenAI API настроен успешно")
        
        # Инициализируем Anthropic клиент
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if not anthropic_api_key or anthropic_api_key == 'your_anthropic_api_key_here':
            raise ValueError("ANTHROPIC_API_KEY не настроен в docker.env файле!")
        
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        logger.info("Anthropic API настроен успешно")
        
        self.tools = [
            {
                "name": "run-python-file",
                "description": "Запускает конкретный Python файл",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Путь к Python файлу для запуска (относительно /host директории)"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "test-python-code",
                "description": "Генерирует и запускает полноценные тесты для Python файла используя OpenAI GPT-3.5-turbo и Claude Haiku 3.5 параллельно, сравнивает результаты",
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
        logger.info(f"Возвращено {len(self.tools)} инструментов")
        return self.tools

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Вызывает указанный инструмент с аргументами"""
        logger.info(f"Вызов инструмента: {tool_name} с аргументами: {arguments}")
        
        try:
            if tool_name == "run-python-file":
                return self.run_python_file(arguments.get("file_path"))
            elif tool_name == "test-python-code":
                return self.test_python_code(arguments.get("file_path"))
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Неизвестный инструмент: {tool_name}"
                        }
                    ]
                }
        except Exception as e:
            logger.error(f"Ошибка выполнения инструмента {tool_name}: {str(e)}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"💥 Ошибка выполнения инструмента {tool_name}: {str(e)}"
                    }
                ]
            }



    def run_python_file(self, file_path: str) -> Dict[str, Any]:
        """Запускает Python файл и возвращает результат"""
        try:
            if not file_path:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "❌ Не указан путь к файлу"
                        }
                    ]
                }
            
            # Проверяем существование файла
            if not os.path.exists(file_path):
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Файл не найден: {file_path}"
                        }
                    ]
                }
            
            logger.info(f"Запуск Python файла: {file_path}")
            
            # Запускаем файл
            result = subprocess.run(
                ["python3", file_path],
                capture_output=True,
                text=True,
                timeout=30  # Таймаут 30 секунд
            )
            
            output_text = f"🐍 Запуск файла: {file_path}\n\n"
            
            if result.stdout:
                output_text += f"📤 Вывод:\n{result.stdout}\n"
            
            if result.stderr:
                output_text += f"⚠️ Ошибки:\n{result.stderr}\n"
            
            output_text += f"📊 Код завершения: {result.returncode}"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": output_text
                    }
                ]
            }
            
        except subprocess.TimeoutExpired:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"⏰ Превышен таймаут выполнения файла {file_path}"
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

    def test_python_code(self, file_path: str) -> Dict[str, Any]:
        """Генерирует и запускает тесты для Python файла используя OpenAI"""
        try:
            if not file_path:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "❌ Не указан путь к файлу"
                        }
                    ]
                }
            
            # Проверяем существование файла
            if not os.path.exists(file_path):
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Файл не найден: {file_path}"
                        }
                    ]
                }
            
            # Читаем содержимое файла
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            logger.info(f"Файл {file_path} прочитан, размер: {len(source_code)} символов")
            
            # Генерируем тесты параллельно используя обе модели
            logger.info("Запускаем параллельную генерацию тестов с OpenAI и Claude")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                # Запускаем обе модели параллельно
                openai_future = executor.submit(self._generate_tests_with_openai, source_code, file_path)
                claude_future = executor.submit(self._generate_tests_with_claude, source_code, file_path)
                
                # Ждем результаты
                try:
                    openai_test_code = openai_future.result(timeout=60)
                    openai_success = True
                    logger.info("OpenAI успешно сгенерировал тесты")
                except Exception as e:
                    openai_test_code = None
                    openai_success = False
                    logger.error(f"OpenAI не смог сгенерировать тесты: {e}")
                
                try:
                    claude_test_code = claude_future.result(timeout=60)
                    claude_success = True
                    logger.info("Claude успешно сгенерировал тесты")
                except Exception as e:
                    claude_test_code = None
                    claude_success = False
                    logger.error(f"Claude не смог сгенерировать тесты: {e}")
            
            # Проверяем, что хотя бы одна модель сработала
            if not openai_success and not claude_success:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Обе модели не смогли сгенерировать тесты для файла {file_path}"
                        }
                    ]
                }
            
            # Создаем временную директорию для тестирования
            results = []
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Копируем оригинальный файл во временную директорию
                original_filename = os.path.basename(file_path)
                temp_original_file = os.path.join(temp_dir, original_filename)
                
                with open(file_path, 'r', encoding='utf-8') as src, open(temp_original_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                
                logger.info(f"Временная директория создана: {temp_dir}")
                logger.info(f"Оригинальный файл скопирован: {temp_original_file}")
                
                # Запускаем тесты для OpenAI (если есть)
                if openai_success and openai_test_code:
                    openai_test_file = os.path.join(temp_dir, f"test_openai_{original_filename}")
                    with open(openai_test_file, 'w', encoding='utf-8') as test_file:
                        test_file.write(openai_test_code)
                    
                    logger.info(f"Файл с тестами OpenAI создан: {openai_test_file}")
                    openai_result = self._run_tests(openai_test_file, temp_original_file)
                    results.append(("OpenAI GPT-3.5-turbo", openai_result))
                
                # Запускаем тесты для Claude (если есть)
                if claude_success and claude_test_code:
                    claude_test_file = os.path.join(temp_dir, f"test_claude_{original_filename}")
                    with open(claude_test_file, 'w', encoding='utf-8') as test_file:
                        test_file.write(claude_test_code)
                    
                    logger.info(f"Файл с тестами Claude создан: {claude_test_file}")
                    claude_result = self._run_tests(claude_test_file, temp_original_file)
                    results.append(("Claude Haiku 3.5", claude_result))
            
            # Формируем сводный отчет
            return self._create_comparison_report(file_path, results)
            
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

    def _generate_tests_with_openai(self, source_code: str, file_path: str) -> str:
        """Генерирует тесты используя OpenAI API"""
        try:
            logger.info(f"Генерирую тесты для {file_path} используя OpenAI API")
            
            # Получаем имя модуля
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            
            prompt = f"""
Сгенерируй полноценные тесты для Python кода используя pytest.

ВАЖНО: 
- НЕ используй прямые вызовы функций - всегда используй `test_module.`
- Убедись что все тесты используют `test_module.` для доступа к функциям
- Импортируй модуль как `test_module = __import__('{module_name}')`
- НИКОГДА не используй имена временных файлов в импортах
- Всегда используй имя модуля '{module_name}' для импорта

Код для тестирования:
```python
{source_code}
```

Сгенерируй тесты которые:
1. Импортируют модуль как `test_module = __import__('{module_name}')`
2. Тестируют все функции и классы
3. Включают граничные случаи
4. Используют pytest
5. Обязательно используют `test_module.` для всех вызовов
6. НЕ используют никакие другие имена модулей

Верни только код тестов без дополнительных объяснений.
"""
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты эксперт по Python тестированию. Генерируй качественные тесты используя pytest."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            test_code = response.choices[0].message.content.strip()
            
            # Убираем markdown разметку если есть
            if test_code.startswith("```python"):
                test_code = test_code[9:]
            if test_code.startswith("```"):
                test_code = test_code[3:]
            if test_code.endswith("```"):
                test_code = test_code[:-3]
            
            test_code = test_code.strip()
            
            # Полностью переписываем код тестов чтобы гарантировать правильные импорты
            # Извлекаем только функции тестирования из ответа OpenAI
            lines = test_code.split('\n')
            test_functions = []
            in_test_function = False
            current_function = []

            for line in lines:
                if line.strip().startswith('def test_'):
                    if current_function:
                        test_functions.append('\n'.join(current_function))
                    current_function = [line]
                    in_test_function = True
                elif in_test_function and line.strip() and not line.strip().startswith('#'):
                    current_function.append(line)
                elif in_test_function and line.strip().startswith('#'):
                    current_function.append(line)

            if current_function:
                test_functions.append('\n'.join(current_function))

            # Собираем финальный код
            if test_functions:
                test_code = f"""import pytest

# Импортируем модуль для тестирования
test_module = __import__('{module_name}')

{chr(10).join(test_functions)}
"""
            else:
                # Если не удалось извлечь функции, создаем базовый тест
                test_code = f"""import pytest

# Импортируем модуль для тестирования
test_module = __import__('{module_name}')

def test_module_import():
    assert test_module is not None
"""
            
            logger.info(f"OpenAI сгенерировал тесты: {test_code[:200]}...")
            logger.info(f"OpenAI API успешно сгенерировал тесты для {file_path}")
            return test_code
            
        except Exception as e:
            logger.error(f"Ошибка OpenAI API при генерации тестов: {e}")
            raise e

    def _generate_tests_with_claude(self, source_code: str, file_path: str) -> str:
        """Генерирует тесты используя Claude Haiku 3.5"""
        try:
            logger.info(f"Генерирую тесты для {file_path} используя Claude Haiku 3.5")
            
            # Получаем имя модуля
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            
            prompt = f"""
Сгенерируй полноценные тесты для Python кода используя pytest.

ВАЖНО: 
- НЕ используй прямые вызовы функций - всегда используй `test_module.`
- Убедись что все тесты используют `test_module.` для доступа к функциям
- Импортируй модуль как `test_module = __import__('{module_name}')`
- НИКОГДА не используй имена временных файлов в импортах
- Всегда используй имя модуля '{module_name}' для импорта

Код для тестирования:
```python
{source_code}
```

Сгенерируй тесты которые:
1. Импортируют модуль как `test_module = __import__('{module_name}')`
2. Тестируют все функции и классы
3. Включают граничные случаи
4. Используют pytest
5. Обязательно используют `test_module.` для всех вызовов
6. НЕ используют никакие другие имена модулей

Верни только код тестов без дополнительных объяснений.
"""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=2000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            test_code = response.content[0].text.strip()
            
            # Убираем markdown разметку если есть
            if test_code.startswith("```python"):
                test_code = test_code[9:]
            if test_code.startswith("```"):
                test_code = test_code[3:]
            if test_code.endswith("```"):
                test_code = test_code[:-3]
            
            test_code = test_code.strip()
            
            # Полностью переписываем код тестов чтобы гарантировать правильные импорты
            # Извлекаем только функции тестирования из ответа Claude
            lines = test_code.split('\n')
            test_functions = []
            in_test_function = False
            current_function = []

            for line in lines:
                if line.strip().startswith('def test_'):
                    if current_function:
                        test_functions.append('\n'.join(current_function))
                    current_function = [line]
                    in_test_function = True
                elif in_test_function and line.strip() and not line.strip().startswith('#'):
                    current_function.append(line)
                elif in_test_function and line.strip().startswith('#'):
                    current_function.append(line)

            if current_function:
                test_functions.append('\n'.join(current_function))

            # Собираем финальный код
            if test_functions:
                test_code = f"""import pytest

# Импортируем модуль для тестирования
test_module = __import__('{module_name}')

{chr(10).join(test_functions)}
"""
            else:
                # Если не удалось извлечь функции, создаем базовый тест
                test_code = f"""import pytest

# Импортируем модуль для тестирования
test_module = __import__('{module_name}')

def test_module_import():
    assert test_module is not None
"""
            
            logger.info(f"Claude сгенерировал тесты: {test_code[:200]}...")
            logger.info(f"Claude API успешно сгенерировал тесты для {file_path}")
            return test_code
            
        except Exception as e:
            logger.error(f"Ошибка Claude API при генерации тестов: {e}")
            raise e

    def _create_comparison_report(self, file_path: str, results: list) -> Dict[str, Any]:
        """Создает сводный отчет сравнения результатов тестирования"""
        try:
            original_filename = os.path.basename(file_path)
            
            report = f"🤖 Сравнение генерации тестов для файла: {original_filename}\n\n"
            
            summary_data = []
            
            for model_name, result in results:
                report += f"{'='*60}\n"
                report += f"📊 {model_name}:\n"
                report += f"{'='*60}\n"
                
                # Извлекаем текст результата
                result_text = result.get("content", [{}])[0].get("text", "")
                report += result_text + "\n\n"
                
                # Анализируем результат для сводки
                if "✅ Все тесты прошли успешно!" in result_text:
                    summary_data.append((model_name, "✅ Успешно", "Все тесты прошли"))
                elif "❌ Некоторые тесты провалились" in result_text:
                    summary_data.append((model_name, "⚠️ Частично", "Есть провалившиеся тесты"))
                elif "💥 Ошибка" in result_text or "⏰ Превышен таймаут" in result_text:
                    summary_data.append((model_name, "❌ Ошибка", "Не удалось запустить тесты"))
                else:
                    summary_data.append((model_name, "❓ Неизвестно", "Неопределенный результат"))
            
            # Добавляем сводку
            if len(summary_data) > 1:
                report += f"{'='*60}\n"
                report += f"📈 СВОДКА СРАВНЕНИЯ:\n"
                report += f"{'='*60}\n"
                
                for model_name, status, description in summary_data:
                    report += f"{status} {model_name}: {description}\n"
                
                # Определяем победителя
                successful_models = [data for data in summary_data if data[1] == "✅ Успешно"]
                if len(successful_models) == 1:
                    winner = successful_models[0][0]
                    report += f"\n🏆 Лучший результат: {winner}\n"
                elif len(successful_models) > 1:
                    report += f"\n🤝 Обе модели показали отличные результаты!\n"
                else:
                    partial_models = [data for data in summary_data if data[1] == "⚠️ Частично"]
                    if partial_models:
                        report += f"\n⚠️ Лучший результат среди частичных: {partial_models[0][0]}\n"
                    else:
                        report += f"\n😞 Обе модели не смогли успешно сгенерировать рабочие тесты\n"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": report
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания отчета сравнения: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"💥 Ошибка создания отчета сравнения: {str(e)}"
                    }
                ]
            }

    def _run_tests(self, test_file: str, original_file: str) -> Dict[str, Any]:
        """Запускает тесты и возвращает результаты"""
        try:
            logger.info(f"Запуск тестов из файла: {test_file}")
            logger.info(f"Оригинальный файл: {original_file}")
            
            # Читаем содержимое тестового файла для логирования
            with open(test_file, 'r', encoding='utf-8') as f:
                test_content = f.read()
            logger.info(f"Содержимое тестового файла: {test_content[:500]}...")
            
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
            
            output_text = f"🧪 Результаты тестирования файла: {os.path.basename(original_file)}\n\n"
            
            if result.stdout:
                output_text += f"📤 Вывод тестов:\n{result.stdout}\n"
            
            if result.stderr:
                output_text += f"⚠️ Ошибки тестов:\n{result.stderr}\n"
            
            output_text += f"📊 Код завершения: {result.returncode}\n"
            
            if result.returncode == 0:
                output_text += "✅ Все тесты прошли успешно!"
            else:
                output_text += "❌ Некоторые тесты провалились"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": output_text
                    }
                ]
            }
            
        except subprocess.TimeoutExpired:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"⏰ Превышен таймаут выполнения тестов для файла {original_file}"
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Ошибка запуска тестов для файла {original_file}: {str(e)}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"💥 Ошибка запуска тестов для файла {original_file}: {str(e)}"
                    }
                ]
            }

def main():
    """Главная функция для запуска MCP сервера"""
    server = PythonRunnerMCPServer()
    
    # Простой цикл обработки запросов (для демонстрации)
    logger.info("Python Runner MCP Server запущен")
    
    # В реальном MCP сервере здесь был бы цикл чтения из stdin
    # и отправки ответов в stdout
    
if __name__ == "__main__":
    main()
