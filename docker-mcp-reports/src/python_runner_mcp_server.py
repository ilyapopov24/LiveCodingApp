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
import requests
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

def debug_print(message: str):
    """Принудительный вывод в stdout и stderr для лучшей видимости в Docker"""
    print(message)
    import sys
    sys.stderr.write(f"{message}\n")
    sys.stderr.flush()

class PythonRunnerMCPServer:
    """MCP сервер для запуска Python файлов и генерации тестов"""
    
    def __init__(self):
        # Загружаем переменные окружения
        load_dotenv('docker-settings.env')
        
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
        
        # Настройка Ollama для локальных моделей
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://ollama-server:11434')
        logger.info(f"Ollama настроен на: {self.ollama_base_url}")
        
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
            },
            {
                "name": "fix-android-bug",
                "description": "Анализирует Android проект и исправляет указанный баг используя Claude AI",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Путь к Android проекту (например: /host/test-project)"
                        },
                        "bug_description": {
                            "type": "string",
                            "description": "Описание бага для исправления"
                        }
                    },
                    "required": ["project_path", "bug_description"]
                }
            },
            {
                "name": "build-android-pipeline",
                "description": "Запускает Android debug build pipeline через GitHub Actions",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
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
            elif tool_name == "fix-android-bug":
                return self.fix_android_bug(
                    arguments.get("project_path"), 
                    arguments.get("bug_description")
                )
            elif tool_name == "build-android-pipeline":
                return self.build_android_pipeline()
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
            
            # Генерируем тесты параллельно используя три модели
            logger.info("Запускаем параллельную генерацию тестов с OpenAI, Claude и Ollama Qwen:06")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                # Запускаем три модели параллельно
                openai_future = executor.submit(self._generate_tests_with_openai, source_code, file_path)
                claude_future = executor.submit(self._generate_tests_with_claude, source_code, file_path)
                ollama_future = executor.submit(self._generate_tests_with_ollama, source_code, file_path)
                
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
                
                try:
                    ollama_test_code = ollama_future.result(timeout=120)  # Больше времени для локальной модели
                    ollama_success = True
                    logger.info("Ollama Qwen:06 успешно сгенерировал тесты")
                except Exception as e:
                    ollama_test_code = None
                    ollama_success = False
                    logger.error(f"Ollama не смог сгенерировать тесты: {e}")
            
            # Проверяем, что хотя бы одна модель сработала
            if not openai_success and not claude_success and not ollama_success:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Все модели не смогли сгенерировать тесты для файла {file_path}"
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
                
                # Запускаем тесты для Ollama (если есть)
                if ollama_success and ollama_test_code:
                    ollama_test_file = os.path.join(temp_dir, f"test_ollama_{original_filename}")
                    with open(ollama_test_file, 'w', encoding='utf-8') as test_file:
                        test_file.write(ollama_test_code)
                    
                    logger.info(f"Файл с тестами Ollama создан: {ollama_test_file}")
                    ollama_result = self._run_tests(ollama_test_file, temp_original_file)
                    results.append(("Ollama Qwen:06", ollama_result))
            
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
            # Получаем значения из переменных окружения
            openai_max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', 2000))
            openai_temperature = float(os.getenv('OPENAI_TEMPERATURE', 0.3))
            
            logger.info(f"Генерирую тесты для {file_path} используя OpenAI API")
            logger.info(f"OpenAI параметры: max_tokens={openai_max_tokens}, temperature={openai_temperature}")
            
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
2. ПОКРЫВАЮТ ВСЕ ПУБЛИЧНЫЕ МЕТОДЫ И ГРАНИЧНЫЕ СЛУЧАИ
3. Тестируют каждый метод с несколькими наборами входных данных
4. Включают позитивные и негативные сценарии
5. Тестируют граничные значения и исключения
6. Добавляют тесты для валидации входных параметров
7. Тестируют все ветки условных операторов
8. Добавляют тесты для различных типов данных
9. Тестируют взаимодействие между компонентами
10. Тестируют состояния объектов до и после операций
11. Используют pytest
12. Обязательно используют `test_module.` для всех вызовов
13. НЕ используют никакие другие имена модулей

Верни только код тестов без дополнительных объяснений.
"""
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты эксперт по Python тестированию. Генерируй качественные тесты используя pytest."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=openai_max_tokens,
                temperature=openai_temperature
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

    def _generate_tests_with_ollama(self, source_code: str, file_path: str) -> str:
        """Генерирует тесты используя Ollama с локальной моделью Qwen:06"""
        try:
            # Получаем значения из переменных окружения
            ollama_max_tokens = int(os.getenv('OLLAMA_MAX_TOKENS', 4000))
            ollama_temperature = float(os.getenv('OLLAMA_TEMPERATURE', 0.3))
            
            logger.info(f"Генерирую тесты для {file_path} используя Ollama Llama2:7b")
            logger.info(f"Ollama параметры: max_tokens={ollama_max_tokens}, temperature={ollama_temperature}")
            
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
2. ПОКРЫВАЮТ ВСЕ ПУБЛИЧНЫЕ МЕТОДЫ И ГРАНИЧНЫЕ СЛУЧАИ
3. Тестируют каждый метод с несколькими наборами входных данных
4. Включают позитивные и негативные сценарии
5. Тестируют граничные значения и исключения
6. Добавляют тесты для валидации входных параметров
7. Тестируют все ветки условных операторов
8. Добавляют тесты для различных типов данных
9. Тестируют взаимодействие между компонентами
10. Тестируют состояния объектов до и после операций
11. Используют pytest
12. Обязательно используют `test_module.` для всех вызовов
13. НЕ используют никакие другие имена модулей

Верни только код тестов без дополнительных объяснений.
"""
            
            logger.info(f"Отправляю запрос к Ollama API: {self.ollama_base_url}")
            logger.info(f"Промпт для Ollama: {prompt[:200]}...")
            
            # Отправляем запрос к Ollama API
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": "llama2:7b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": ollama_temperature,
                        "num_predict": ollama_max_tokens,
                        "num_ctx": 8192
                    }
                },
                timeout=300
            )
            
            logger.info(f"Ollama ответил со статусом: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Ollama API ошибка: {response.status_code} - {response.text}")
                raise Exception(f"Ollama API ошибка: {response.status_code} - {response.text}")
            
            response_data = response.json()
            logger.info(f"Ollama response_data: {str(response_data)[:200]}...")
            test_code = response_data.get("response", "").strip()
            
            # Убираем markdown разметку если есть
            if test_code.startswith("```python"):
                test_code = test_code[9:]
            if test_code.startswith("```"):
                test_code = test_code[3:]
            if test_code.endswith("```"):
                test_code = test_code[:-3]
            
            test_code = test_code.strip()
            
            # Полностью переписываем код тестов чтобы гарантировать правильные импорты
            # Извлекаем только функции тестирования из ответа Ollama
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
            
            logger.info(f"Ollama Llama2:7b сгенерировал тесты: {test_code[:200]}...")
            logger.info(f"Ollama API успешно сгенерировал тесты для {file_path}")
            return test_code
            
        except Exception as e:
            logger.error(f"Ошибка Ollama API при генерации тестов: {e}")
            raise e

    def _generate_tests_with_claude(self, source_code: str, file_path: str) -> str:
        """Генерирует тесты используя Claude Haiku 3.5"""
        try:
            # Получаем значения из переменных окружения
            anthropic_max_tokens = int(os.getenv('ANTHROPIC_MAX_TOKENS', 2000))
            anthropic_temperature = float(os.getenv('ANTHROPIC_TEMPERATURE', 0.3))
            
            logger.info(f"Генерирую тесты для {file_path} используя Claude Haiku 3.5")
            logger.info(f"Claude параметры: max_tokens={anthropic_max_tokens}, temperature={anthropic_temperature}")
            
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
2. ПОКРЫВАЮТ ВСЕ ПУБЛИЧНЫЕ МЕТОДЫ И ГРАНИЧНЫЕ СЛУЧАИ
3. Тестируют каждый метод с несколькими наборами входных данных
4. Включают позитивные и негативные сценарии
5. Тестируют граничные значения и исключения
6. Добавляют тесты для валидации входных параметров
7. Тестируют все ветки условных операторов
8. Добавляют тесты для различных типов данных
9. Тестируют взаимодействие между компонентами
10. Тестируют состояния объектов до и после операций
11. Используют pytest
12. Обязательно используют `test_module.` для всех вызовов
13. НЕ используют никакие другие имена модулей

Верни только код тестов без дополнительных объяснений.
"""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=anthropic_max_tokens,
                temperature=anthropic_temperature,
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

    def fix_android_bug(self, project_path: str, bug_description: str) -> Dict[str, Any]:
        """Анализирует Android проект и исправляет указанный баг используя Claude AI"""
        
        # ПРОСТОЙ PRINT ДЛЯ ЛОГОВ В DOCKER
        print("="*50)
        print("🚀 НАЧАЛО ВЫПОЛНЕНИЯ fix-android-bug")
        print(f"📁 Путь к проекту: {project_path}")
        print(f"🐛 Описание бага: {bug_description}")
        print("="*50)
        
        try:
            # ПРИНУДИТЕЛЬНЫЙ ВЫВОД НАСТРОЕК НЕЙРОНКИ
            debug_print("🚀 НАЧАЛО ВЫПОЛНЕНИЯ fix-android-bug")
            debug_print(f"📁 Путь к проекту: {project_path}")
            debug_print(f"🐛 Описание бага: {bug_description}")
            
            # Получаем настройки нейронки из переменных окружения
            anthropic_temperature = os.getenv('ANTHROPIC_TEMPERATURE', '0.8')
            anthropic_max_tokens = os.getenv('ANTHROPIC_MAX_TOKENS', '4000')
            debug_print(f"🌡️ ANTHROPIC_TEMPERATURE: {anthropic_temperature}")
            debug_print(f"🎯 ANTHROPIC_MAX_TOKENS: {anthropic_max_tokens}")
            
            # ДУБЛИРУЕМ В PRINT ДЛЯ DOCKER ЛОГОВ
            print(f"🌡️ ANTHROPIC_TEMPERATURE: {anthropic_temperature}")
            print(f"🎯 ANTHROPIC_MAX_TOKENS: {anthropic_max_tokens}")
            
            logger.info(f"Анализ Android проекта: {project_path}")
            logger.info(f"Описание бага: {bug_description}")
            
            if not project_path or not bug_description:
                error_msg = "❌ ОШИБКА: Не указан путь к проекту или описание бага"
                debug_print(error_msg)
                print(error_msg)  # Дублируем в print
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": error_msg
                        }
                    ]
                }
            
            # Проверяем существование директории проекта
            if not os.path.exists(project_path):
                error_msg = f"❌ ОШИБКА: Директория проекта не найдена: {project_path}"
                debug_print(error_msg)
                print(error_msg)  # Дублируем в print
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": error_msg
                        }
                    ]
                }
            
            success_msg = "✅ Директория проекта найдена, начинаю сбор файлов..."
            debug_print(success_msg)
            print(success_msg)  # Дублируем в print
            
            # Собираем все исходные файлы проекта
            project_files = self._collect_android_project_files(project_path)
            
            if not project_files:
                error_msg = "❌ ОШИБКА: Не найдены исходные файлы в проекте"
                debug_print(error_msg)
                print(error_msg)  # Дублируем в print
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": error_msg
                        }
                    ]
                }
            
            # Добавляем логи фильтрации в ответ
            debug_print("📊 СТАТИСТИКА ФИЛЬТРАЦИИ:")
            print("📊 СТАТИСТИКА ФИЛЬТРАЦИИ:")  # Дублируем в print
            # Убираем неправильный подсчет - используем только правильный из _collect_android_project_files
            debug_print(f"   Включено в анализ: {len(project_files)}")
            print(f"   Включено в анализ: {len(project_files)}")  # Дублируем в print
            
            success_msg = f"✅ Найдено {len(project_files)} файлов для анализа"
            debug_print(success_msg)
            print(success_msg)  # Дублируем в print
            logger.info(f"Найдено {len(project_files)} файлов для анализа")
            
            # Отправляем в Claude AI для анализа и исправления
            debug_print("🤖 Отправляю в Claude AI для анализа...")
            print("🤖 Отправляю в Claude AI для анализа...")  # Дублируем в print
            
            # Получаем результат
            fixed_code = self._analyze_and_fix_with_claude(project_files, bug_description)
            
            debug_print("✅ Claude AI завершил анализ")
            print("✅ Claude AI завершил анализ")  # Дублируем в print
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": fixed_code
                    }
                ]
            }
            
        except Exception as e:
            error_msg = f"💥 КРИТИЧЕСКАЯ ОШИБКА: {str(e)}"
            debug_print(error_msg)
            print(error_msg)  # Дублируем в print
            logger.error(f"Ошибка анализа Android проекта: {str(e)}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": error_msg
                    }
                ]
            }

    def _collect_android_project_files(self, project_path: str) -> Dict[str, str]:
        """Собирает исходные файлы Android проекта с умной фильтрацией для экономии токенов"""
        project_files = {}
        
        # Расширения файлов для анализа (только важные)
        extensions = ['.kt', '.java']  # Убираем .xml, .gradle - они не нужны для анализа бага
        
        # Директории для исключения (экономия токенов)
        EXCLUDED_DIRS = ['build', '.gradle', 'gradle', '.idea', '__pycache__', '~', 
                        'node_modules', '.git', 'target', 'bin', 'obj', 'Debug', 'Release']
        
        # Счетчики для отслеживания
        total_files = 0
        excluded_count = 0
        
        logger.info(f"🔍 Начинаю сбор файлов проекта: {project_path}")
        
        for root, dirs, files in os.walk(project_path):
            # Фильтруем директории для следующих итераций
            dirs[:] = [d for d in dirs if not (
                d.startswith('.') or 
                d in ['build', 'gradle', '.gradle', 'node_modules', 'target', 'bin', 'obj'] or
                d in EXCLUDED_DIRS
            )]
            
            # ПРОВЕРЯЕМ ТЕКУЩУЮ ДИРЕКТОРИЮ root
            rel_root = os.path.relpath(root, project_path)
            if any(excluded_dir in rel_root.split(os.sep) for excluded_dir in EXCLUDED_DIRS):
                # Пропускаем файлы из исключенных директорий
                continue
            
            for file in files:
                total_files += 1
                
                # Проверяем расширение
                if not any(file.endswith(ext) for ext in extensions):
                    excluded_count += 1
                    continue
                
                # Проверяем путь
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_path)
                
                # Дополнительная проверка пути
                if any(excluded_dir in rel_path.split(os.sep) for excluded_dir in EXCLUDED_DIRS):
                    excluded_count += 1
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # УМНАЯ ФИЛЬТРАЦИЯ: исключаем ненужные файлы для анализа бага
                    if any(exclude_pattern in rel_path.lower() for exclude_pattern in [
                        'test', 'androidtest', 'example', 'drawable', 'values', 'mipmap', 
                        'xml/', 'res/', 'config', 'rules', 'security', 'backup'
                    ]):
                        excluded_count += 1
                        continue
                    
                    # Добавляем в результат только важные файлы
                    project_files[rel_path] = content
                    
                except Exception as e:
                    logger.warning(f"Не удалось прочитать файл {file_path}: {e}")
                    excluded_count += 1
        
        # Логируем статистику фильтрации
        logger.info(f"📊 СТАТИСТИКА ФИЛЬТРАЦИИ:")
        logger.info(f"   Всего файлов: {total_files}")
        logger.info(f"   Исключено: {excluded_count}")
        logger.info(f"   Включено в анализ: {len(project_files)}")
        
        print(f"📊 СТАТИСТИКА ФИЛЬТРАЦИИ:")
        print(f"   Всего файлов: {total_files}")
        print(f"   Исключено: {excluded_count}")
        print(f"   Включено в анализ: {len(project_files)}")
        
        return project_files

    def _analyze_and_fix_with_claude(self, project_files: Dict[str, str], bug_description: str) -> str:
        """Анализирует проект и исправляет баг используя Claude AI"""
        try:
            # Формируем промпт для Claude
            project_summary = "\n".join([f"📁 {path}:\n```\n{content}\n```" for path, content in project_files.items()])
            
            prompt = f"""
Ты - эксперт по Android разработке. Проанализируй следующий Android проект и исправь указанный баг.

ОПИСАНИЕ БАГА:
{bug_description}

ИСХОДНЫЙ КОД ПРОЕКТА:
{project_summary}

ЗАДАЧА:
1. Проанализируй код и найди причину бага
2. Предложи исправление
3. Покажи исправленный код с объяснением изменений

ВАЖНО:
- Используй только существующие Android API и библиотеки
- Не придумывай несуществующие методы или классы
- Объясни, что именно было исправлено
- Покажи diff изменений

Формат ответа:
🔍 АНАЛИЗ БАГА:
[Твое объяснение проблемы]

🛠️ ИСПРАВЛЕНИЕ:
[Объяснение исправления]

📝 ИСПРАВЛЕННЫЙ КОД:
[Покажи только измененные файлы с исправлениями]

✅ РЕЗУЛЬТАТ:
[Что исправлено и как проверить]
"""
            
            # Получаем значения из переменных окружения
            anthropic_max_tokens = int(os.getenv('ANTHROPIC_MAX_TOKENS', 4000))
            anthropic_temperature = float(os.getenv('ANTHROPIC_TEMPERATURE', 0.8))
            
            # Принудительный вывод для отладки в Docker
            debug_print(f"🔧 Claude AI параметры: max_tokens={anthropic_max_tokens}, temperature={anthropic_temperature}")
            debug_print(f"📏 Размер промпта: {len(prompt)} символов")
            debug_print(f"📁 Количество файлов для анализа: {len(project_files)}")
            
            # Отправляем в Claude AI
            response = self.anthropic_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=anthropic_max_tokens,
                temperature=anthropic_temperature,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            # Логируем информацию о токенах
            if hasattr(response, 'usage'):
                input_tokens = getattr(response.usage, 'input_tokens', 0)
                output_tokens = getattr(response.usage, 'output_tokens', 0)
                total_tokens = getattr(response.usage, 'total_tokens', 0)
                
                # Примерная стоимость (Claude Haiku 3.5: $0.25/1M input, $1.25/1M output)
                estimated_cost = (input_tokens * 0.25 / 1_000_000) + (output_tokens * 1.25 / 1_000_000)
                
                # Принудительный вывод токенов
                debug_print(f"🎯 Токены Claude AI: input={input_tokens}, output={output_tokens}, total={total_tokens}")
                debug_print(f"💰 Примерная стоимость: ${estimated_cost:.6f}")
            else:
                debug_print("⚠️ Информация о токенах недоступна в ответе Claude AI")
            
            result = response.content[0].text.strip()
            logger.info(f"Claude AI проанализировал проект и предложил исправления")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка анализа через Claude AI: {str(e)}")
            return f"💥 Ошибка анализа через Claude AI: {str(e)}"

    def build_android_pipeline(self) -> Dict[str, Any]:
        """Запускает Android debug build pipeline"""
        try:
            logger.info("🚀 Запуск Android debug build pipeline")
            
            # Путь к проекту в volume mount
            project_path = "/host"
            workflow_file = os.path.join(project_path, ".github/workflows/android-debug-build.yml")
            
            # Проверяем существование workflow файла
            if not os.path.exists(workflow_file):
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "❌ Workflow файл не найден: .github/workflows/android-debug-build.yml"
                        }
                    ]
                }
            
            # Получаем GitHub токен из переменных окружения
            github_token = os.getenv('GITHUB_TOKEN')
            if not github_token:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "❌ GITHUB_TOKEN не настроен. Добавьте токен в .env файл для запуска сборки."
                        }
                    ]
                }
            
            # Пытаемся запустить workflow через GitHub API
            try:
                logger.info("Импортируем PyGithub...")
                from github import Github
                logger.info("PyGithub импортирован успешно")
                
                # Инициализируем GitHub клиент
                logger.info(f"Инициализируем GitHub клиент с токеном: {github_token[:10]}...")
                g = Github(github_token)
                logger.info("GitHub клиент инициализирован")
                
                # Получаем информацию о репозитории из git config
                git_config_path = os.path.join(project_path, ".git/config")
                logger.info(f"Проверяем git config: {git_config_path}")
                
                if os.path.exists(git_config_path):
                    logger.info("Git config найден, читаем содержимое...")
                    with open(git_config_path, 'r') as f:
                        config_content = f.read()
                    logger.info(f"Git config содержимое: {config_content[:200]}...")
                    
                    # Извлекаем URL репозитория
                    import re
                    url_match = re.search(r'url\s*=\s*(https://github\.com/[^/]+/[^/]+\.git)', config_content)
                    if url_match:
                        repo_url = url_match.group(1)
                        repo_name = repo_url.replace('https://github.com/', '').replace('.git', '')
                        logger.info(f"Найден репозиторий: {repo_name}")
                        
                        # Получаем репозиторий
                        logger.info("Получаем объект репозитория...")
                        repo = g.get_repo(repo_name)
                        logger.info(f"Репозиторий получен: {repo.full_name}")
                        
                        # Запускаем workflow через gh CLI (надежный способ)
                        logger.info("Запускаем workflow через gh CLI...")
                        
                        # Используем subprocess для вызова gh CLI
                        import subprocess
                        
                        # Запускаем gh api для repository_dispatch
                        result = subprocess.run([
                            "gh", "api", f"repos/{repo_name}/dispatches",
                            "--method", "POST",
                            "-f", "event_type=android-debug-build"
                        ], capture_output=True, text=True, timeout=30)
                        
                        if result.returncode == 0:
                            logger.info("Workflow запущен через gh CLI repository_dispatch успешно!")
                            return {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"✅ Android debug build pipeline запущен!\n\n📱 Сборка началась в репозитории {repo_name}\n🔗 Проверить статус: https://github.com/{repo_name}/actions"
                                    }
                                ]
                            }
                        else:
                            logger.error(f"Ошибка запуска через gh CLI: {result.stderr}")
                            # Fallback: пробуем через API repository_dispatch
                            logger.info("Пробуем через GitHub API repository_dispatch...")
                            try:
                                repo.create_repository_dispatch("android-debug-build", {})
                                logger.info("Workflow запущен через API repository_dispatch успешно!")
                                return {
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": f"✅ Android debug build pipeline запущен!\n\n📱 Сборка началась в репозитории {repo_name}\n🔗 Проверить статус: https://github.com/{repo_name}/actions"
                                        }
                                    ]
                                }
                            except Exception as api_error:
                                logger.error(f"Ошибка через API: {api_error}")
                                return {
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": f"❌ Не удалось запустить workflow. Попробуйте вручную: https://github.com/{repo_name}/actions"
                                        }
                                    ]
                                }
                    
            except ImportError:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "❌ PyGithub не установлен. Установите: pip install PyGithub"
                        }
                    ]
                }
            except Exception as e:
                logger.error(f"Ошибка запуска workflow через GitHub API: {str(e)}")
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"💥 Ошибка запуска workflow: {str(e)}\n\nПопробуйте запустить вручную:\n1. GitHub репозиторий → Actions\n2. Выберите 'Android Debug Build'\n3. Нажмите 'Run workflow'"
                        }
                    ]
                }
                
        except Exception as e:
            logger.error(f"Ошибка запуска Android build pipeline: {str(e)}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"💥 Ошибка запуска Android build pipeline: {str(e)}"
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
