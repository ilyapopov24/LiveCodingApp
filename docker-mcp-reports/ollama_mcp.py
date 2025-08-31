#!/usr/bin/env python3
"""
Простой MCP сервер для Ollama
"""

import json
import subprocess
import sys
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_ollama_command(command):
    """Выполнить команду Ollama"""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def main():
    """Основная функция MCP сервера"""
    
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
                            "tools": {
                                "list-models": {
                                    "name": "list-models",
                                    "description": "Показать список доступных моделей Ollama",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {},
                                        "required": []
                                    }
                                },
                                "run-model": {
                                    "name": "run-model",
                                    "description": "Запустить модель Ollama с запросом",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "model": {
                                                "type": "string",
                                                "description": "Название модели"
                                            },
                                            "prompt": {
                                                "type": "string",
                                                "description": "Текст запроса"
                                            }
                                        },
                                        "required": ["model", "prompt"]
                                    }
                                }
                            }
                        },
                        "serverInfo": {
                            "name": "ollama-mcp",
                            "version": "1.0.0"
                        }
                    }
                }
                
            elif request.get("method") == "tools/call":
                # Обрабатываем вызов инструмента
                tool_name = request["params"]["tool"]["name"]
                arguments = request["params"]["tool"].get("arguments", {})
                
                if tool_name == "list-models":
                    success, output, error = run_ollama_command(["ollama", "list"])
                    if success:
                        result = {"content": [{"type": "text", "text": f"Доступные модели:\n```\n{output}\n```"}]}
                    else:
                        result = {"content": [{"type": "text", "text": f"Ошибка: {error}"}]}
                        
                elif tool_name == "run-model":
                    model = arguments.get("model", "llama2:7b-optimized")
                    prompt = arguments.get("prompt", "")
                    
                    if not prompt:
                        result = {"content": [{"type": "text", "text": "Ошибка: не указан промпт"}]}
                    else:
                        try:
                            process = subprocess.Popen(
                                ["ollama", "run", model],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                            )
                            stdout, stderr = process.communicate(input=prompt, timeout=300)
                            
                            if process.returncode == 0:
                                result = {"content": [{"type": "text", "text": f"**Ответ модели {model}:**\n\n{stdout.strip()}"}]}
                            else:
                                result = {"content": [{"type": "text", "text": f"Ошибка: {stderr.strip()}"}]}
                        except Exception as e:
                            result = {"content": [{"type": "text", "text": f"Ошибка: {str(e)}"}]}
                else:
                    result = {"content": [{"type": "text", "text": f"Неизвестный инструмент: {tool_name}"}]}
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
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

