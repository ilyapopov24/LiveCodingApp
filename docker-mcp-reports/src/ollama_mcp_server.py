#!/usr/bin/env python3
"""
MCP Server для Ollama - локальные LLM модели
"""

import json
import subprocess
import sys
import requests
from typing import Any, Dict, List, Optional
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaMCPServer:
    def __init__(self):
        self.server_name = "ollama-mcp-server"
        self.server_version = "1.0.0"
        self.ollama_url = "http://ollama-server:11434"
        self.tools = [
            {
                "name": "list-models",
                "description": "Показать список доступных моделей Ollama",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "run-model",
                "description": "Запустить модель Ollama с запросом",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "model": {
                            "type": "string",
                            "description": "Название модели (например, llama2:7b-optimized)"
                        },
                        "prompt": {
                            "type": "string",
                            "description": "Текст запроса для модели"
                        },
                        "max_tokens": {
                            "type": "integer",
                            "description": "Максимальное количество токенов в ответе",
                            "default": 1000
                        }
                    },
                    "required": ["model", "prompt"]
                }
            },
            {
                "name": "pull-model",
                "description": "Загрузить новую модель Ollama",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "model": {
                            "type": "string",
                            "description": "Название модели для загрузки"
                        }
                    },
                    "required": ["model"]
                }
            },
            {
                "name": "model-info",
                "description": "Получить информацию о модели",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "model": {
                            "type": "string",
                            "description": "Название модели"
                        }
                    },
                    "required": ["model"]
                }
            }
        ]

    def _run_ollama_command(self, command: List[str]) -> Dict[str, Any]:
        """Выполнить команду Ollama"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 минут таймаут
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout.strip(),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "output": None,
                    "error": result.stderr.strip()
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": None,
                "error": "Команда превысила таймаут (5 минут)"
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": str(e)
            }

    def list_models(self) -> Dict[str, Any]:
        """Показать список доступных моделей"""
        logger.info("Запрос списка моделей")
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            models = data.get("models", [])
            if models:
                model_list = "\n".join([f"- {model['name']} ({model.get('size', 0) / 1024 / 1024 / 1024:.1f} GB)" for model in models])
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Доступные модели:\n```\n{model_list}\n```"
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "Нет доступных моделей. Используйте pull-model для загрузки модели."
                        }
                    ]
                }
        except Exception as e:
            logger.error(f"Ошибка при получении списка моделей: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Ошибка при получении списка моделей: {str(e)}"
                    }
                ]
            }

    def run_model(self, model: str, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """Запустить модель с запросом"""
        logger.info(f"Запуск модели {model} с запросом: {prompt[:50]}...")
        
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=300
            )
            response.raise_for_status()
            data = response.json()
            
            if "response" in data:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"**Модель {model} отвечает:**\n\n{data['response'].strip()}"
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Неожиданный ответ от модели: {data}"
                        }
                    ]
                }
        except requests.exceptions.Timeout:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Модель превысила таймаут (5 минут)"
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Ошибка при запуске модели: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Ошибка: {str(e)}"
                    }
                ]
            }

    def pull_model(self, model: str) -> Dict[str, Any]:
        """Загрузить новую модель"""
        logger.info(f"Загрузка модели {model}")
        try:
            payload = {"name": model}
            response = requests.post(
                f"{self.ollama_url}/api/pull",
                json=payload,
                timeout=600  # 10 минут для загрузки
            )
            response.raise_for_status()
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Модель {model} успешно загружена!"
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Ошибка при загрузке модели {model}: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Ошибка при загрузке модели {model}: {str(e)}"
                    }
                ]
            }

    def model_info(self, model: str) -> Dict[str, Any]:
        """Получить информацию о модели"""
        logger.info(f"Запрос информации о модели {model}")
        try:
            # Получаем информацию о модели через API
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            models = data.get("models", [])
            model_info = next((m for m in models if m['name'] == model), None)
            
            if model_info:
                info_text = f"""Информация о модели {model}:
- Размер: {model_info.get('size', 0) / 1024 / 1024 / 1024:.1f} GB
- Изменена: {model_info.get('modified_at', 'Неизвестно')}
- Digest: {model_info.get('digest', 'Неизвестно')}
- Формат: {model_info.get('details', {}).get('format', 'Неизвестно')}
- Семейство: {model_info.get('details', {}).get('family', 'Неизвестно')}
- Размер параметров: {model_info.get('details', {}).get('parameter_size', 'Неизвестно')}"""
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": info_text
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Модель {model} не найдена. Используйте list-models для просмотра доступных моделей."
                        }
                    ]
                }
        except Exception as e:
            logger.error(f"Ошибка при получении информации о модели {model}: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Ошибка при получении информации о модели {model}: {str(e)}"
                    }
                ]
            }

    def list_tools(self) -> List[Dict[str, Any]]:
        """Получить список доступных инструментов"""
        return self.tools

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Вызвать инструмент"""
        return self.handle_tool_call(tool_name, arguments)

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Обработать вызов инструмента"""
        try:
            if tool_name == "list-models":
                return self.list_models()
            elif tool_name == "run-model":
                return self.run_model(
                    model=arguments["model"],
                    prompt=arguments["prompt"],
                    max_tokens=arguments.get("max_tokens", 1000)
                )
            elif tool_name == "pull-model":
                return self.pull_model(model=arguments["model"])
            elif tool_name == "model-info":
                return self.model_info(model=arguments["model"])
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Неизвестный инструмент: {tool_name}"
                        }
                    ]
                }
        except Exception as e:
            logger.error(f"Ошибка при обработке инструмента {tool_name}: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Ошибка при выполнении {tool_name}: {str(e)}"
                    }
                ]
            }

def main():
    """Основная функция для STDIO режима"""
    server = OllamaMCPServer()
    
    # Читаем ввод построчно
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            
            if request.get("method") == "initialize":
                # Отправляем capabilities
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {tool["name"]: tool for tool in server.tools}
                        },
                        "serverInfo": {
                            "name": server.server_name,
                            "version": server.server_version
                        }
                    }
                }
            elif request.get("method") == "tools/call":
                # Обрабатываем вызов инструмента
                tool_call = request["params"]["tool"]
                result = server.handle_tool_call(
                    tool_call["name"],
                    tool_call.get("arguments", {})
                )
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": result["content"]
                    }
                }
            else:
                # Неизвестный метод
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": "Method not found"
                    }
                }
            
            # Отправляем ответ
            print(json.dumps(response, ensure_ascii=False))
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            logger.error("Ошибка парсинга JSON")
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            print(json.dumps(response, ensure_ascii=False))
            sys.stdout.flush()

if __name__ == "__main__":
    main()

