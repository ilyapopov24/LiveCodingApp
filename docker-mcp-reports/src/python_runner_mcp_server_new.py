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
                            "description": "Путь к Python файлу для запуска (относительно /host директории)"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "test-python-code",
                "description": "Генерирует и запускает полноценные тесты для Python файла используя OpenAI",
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

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Обрабатывает запрос от MCP клиента"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "tools/list":
                return {
                    "tools": self.tools
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
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
            else:
                return {
                    "error": {
                        "code": -32601,
                        "message": f"Неизвестный метод: {method}"
                    }
                }
        except Exception as e:
            logger.error(f"Ошибка обработки запроса: {str(e)}")
            return {
                "error": {
                    "code": -32603,
                    "message": f"Внутренняя ошибка сервера: {str(e)}"
                }
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
            
            # Генерируем тесты используя OpenAI
            test_code = self._generate_tests_with_openai(source_code, file_path)
            
            if not test_code:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Не удалось сгенерировать тесты для файла {file_path}"
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

Код для тестирования:
```python
{source_code}
```

Сгенерируй тесты которые:
1. Импортируют модуль как `test_module`
2. Тестируют все функции и классы
3. Включают граничные случаи
4. Используют pytest
5. Обязательно используют `test_module.` для всех вызовов

Верни только код тестов без дополнительных объяснений.
"""
            
            response = openai.ChatCompletion.create(
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
            
            # Добавляем импорт модуля если его нет
            if f"test_module = __import__('{module_name}')" not in test_code:
                test_code = f"""import pytest

# Импортируем модуль для тестирования
test_module = __import__('{module_name}')

{test_code}
"""
            
            logger.info(f"OpenAI сгенерировал тесты: {test_code[:200]}...")
            logger.info(f"OpenAI API успешно сгенерировал тесты для {file_path}")
            return test_code
            
        except Exception as e:
            logger.error(f"Ошибка OpenAI API при генерации тестов: {e}")
            raise e

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









