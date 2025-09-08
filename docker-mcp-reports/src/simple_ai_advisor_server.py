#!/usr/bin/env python3
"""
Простой AI Advisor MCP Server для тестирования
Работает без внешних зависимостей
"""

import json
import sys
from typing import Dict, Any

class SimpleAIAdvisorServer:
    def __init__(self):
        self.tools = {
            "analyze_profile": {
                "name": "analyze_profile",
                "description": "Полный анализ GitHub профиля с AI рекомендациями",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub username для анализа"
                        }
                    },
                    "required": ["username"]
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
                            "name": "simple-ai-advisor",
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
                
                if tool_name == "analyze_profile":
                    username = arguments.get("username", "octocat")
                    result = self.analyze_profile(username)
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

    def analyze_profile(self, username: str) -> str:
        """Анализирует GitHub профиль (тестовая версия)"""
        return f"""🤖 **Анализ профиля GitHub: @{username}**

## 📊 Текущее состояние:
- **Пользователь**: {username}
- **Статус**: Активный разработчик
- **Репозитории**: 15+ проектов
- **Звезды**: 250+ звезд
- **Форки**: 50+ форков

## 🎯 Приоритетные области для улучшения:
1. **Профиль и био** - Добавить описание и ссылки
2. **Репозитории** - Улучшить документацию
3. **Активность** - Участвовать в сообществе
4. **Технологии** - Показать современный стек

## 💡 Рекомендации:
- Добавить README с описанием проектов
- Участвовать в open source проектах
- Обновить профиль с контактной информацией
- Добавить скриншоты и демо

## 📅 План на 3 месяца:
- **Месяц 1**: Обновить профиль и README
- **Месяц 2**: Участвовать в сообществе
- **Месяц 3**: Создать портфолио проектов

✅ **Анализ завершен успешно!**"""

def main():
    """Главная функция для работы через STDIO"""
    server = SimpleAIAdvisorServer()
    
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

