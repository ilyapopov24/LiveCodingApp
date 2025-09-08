#!/usr/bin/env python3
"""
Ollama MCP Server для работы через STDIO
Подключается к реальному Ollama серверу
"""

import json
import logging
import os
import sys
import requests
from typing import Dict, Any

# Настройка логирования только для ошибок
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class OllamaSTDIOServer:
    def __init__(self):
        self.ollama_url = "http://ollama-server:11434"
        
        # Регистрируем тулсы
        self.tools = {
            "run-model": {
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
            }
        }

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Обрабатывает MCP запрос"""
        try:
            method = request.get("method")
            
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "ollama-stdio-server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "tools": list(self.tools.values())
                    }
                }
            
            elif method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "run-model":
                    model = arguments.get("model", "llama2:7b-optimized")
                    prompt = arguments.get("prompt", "Привет!")
                    max_tokens = arguments.get("max_tokens", 1000)
                    
                    result = self.run_model(model, prompt, max_tokens)
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": result
                                }
                            ]
                        }
                    }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

    def run_model(self, model: str, prompt: str, max_tokens: int = 1000) -> str:
        """Запускает модель Ollama с запросом"""
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
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            return data.get("response", "Нет ответа от модели")
            
        except requests.exceptions.ConnectionError:
            return f"❌ Не удается подключиться к Ollama серверу по адресу {self.ollama_url}"
        except requests.exceptions.Timeout:
            return "❌ Таймаут при обращении к Ollama серверу"
        except Exception as e:
            return f"❌ Ошибка Ollama: {str(e)}"

def main():
    """Главная функция для работы через STDIO"""
    server = OllamaSTDIOServer()
    
    try:
        # Читаем JSON-RPC запрос из stdin
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
                
            try:
                request = json.loads(line)
                response = server.handle_request(request)
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response, ensure_ascii=False))
                sys.stdout.flush()
                
    except KeyboardInterrupt:
        pass
    except Exception as e:
        error_response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }
        print(json.dumps(error_response, ensure_ascii=False))
        sys.stdout.flush()

if __name__ == "__main__":
    main()