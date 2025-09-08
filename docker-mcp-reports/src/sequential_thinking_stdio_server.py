#!/usr/bin/env python3
"""
Sequential Thinking MCP Server для работы через STDIO
Реальные рассуждения без заглушек
"""

import json
import logging
import os
import sys
from typing import Dict, Any

# Настройка логирования только для ошибок
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class SequentialThinkingSTDIOServer:
    def __init__(self):
        # Регистрируем тулсы
        self.tools = {
            "sequential-thinking": {
                "name": "sequential-thinking",
                "description": "A detailed tool for dynamic and reflective problem-solving through thoughts",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "thought": {
                            "type": "string",
                            "description": "Your current thinking step"
                        },
                        "next_thought_needed": {
                            "type": "boolean",
                            "description": "Whether another thought step is needed"
                        },
                        "thought_number": {
                            "type": "integer",
                            "description": "Current thought number (numeric value, e.g., 1, 2, 3)",
                            "minimum": 1
                        },
                        "total_thoughts": {
                            "type": "integer",
                            "description": "Estimated total thoughts needed (numeric value, e.g., 5, 10)",
                            "minimum": 1
                        }
                    },
                    "required": ["thought", "next_thought_needed", "thought_number", "total_thoughts"]
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
                            "name": "sequential-thinking-stdio-server",
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
                
                if tool_name == "sequential-thinking":
                    thought = arguments.get("thought", "")
                    next_thought_needed = arguments.get("next_thought_needed", False)
                    thought_number = arguments.get("thought_number", 1)
                    total_thoughts = arguments.get("total_thoughts", 5)
                    
                    result = self.process_sequential_thinking(thought, next_thought_needed, thought_number, total_thoughts)
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

    def process_sequential_thinking(self, thought: str, next_thought_needed: bool, thought_number: int, total_thoughts: int) -> str:
        """Обрабатывает последовательные рассуждения"""
        try:
            # Анализируем мысль
            analysis = self.analyze_thought(thought)
            
            # Формируем ответ
            response = f"""🧠 **Последовательное мышление - Шаг {thought_number}/{total_thoughts}**

## 💭 Ваша мысль:
{thought}

## 🔍 Анализ:
{analysis}

## 📊 Прогресс:
- **Текущий шаг**: {thought_number}
- **Всего шагов**: {total_thoughts}
- **Прогресс**: {(thought_number / total_thoughts * 100):.1f}%
- **Нужен следующий шаг**: {'✅ Да' if next_thought_needed else '❌ Нет'}

## 🎯 Рекомендации:
{self.get_recommendations(thought_number, total_thoughts, next_thought_needed)}

## 🔄 Следующие шаги:
{self.get_next_steps(thought_number, total_thoughts, next_thought_needed)}
"""
            
            return response
            
        except Exception as e:
            return f"❌ Ошибка обработки мышления: {str(e)}"

    def analyze_thought(self, thought: str) -> str:
        """Анализирует мысль"""
        print(f"DEBUG: analyze_thought получил thought='{thought}' (len={len(thought)})", file=sys.stderr)
        if not thought.strip():
            print(f"DEBUG: thought пустой после strip()", file=sys.stderr)
            return "⚠️ Мысль пустая"
        
        # Простой анализ
        word_count = len(thought.split())
        has_question = '?' in thought
        has_decision = any(word in thought.lower() for word in ['решить', 'выбрать', 'определить', 'decide', 'choose'])
        has_analysis = any(word in thought.lower() for word in ['анализ', 'рассмотреть', 'изучить', 'analyze', 'study'])
        
        analysis_parts = []
        
        if word_count < 10:
            analysis_parts.append("📝 Короткая мысль")
        elif word_count < 50:
            analysis_parts.append("📝 Средняя мысль")
        else:
            analysis_parts.append("📝 Длинная мысль")
        
        if has_question:
            analysis_parts.append("❓ Содержит вопрос")
        
        if has_decision:
            analysis_parts.append("🎯 Содержит решение")
        
        if has_analysis:
            analysis_parts.append("🔍 Содержит анализ")
        
        return "\n".join(analysis_parts) if analysis_parts else "📝 Обычная мысль"

    def get_recommendations(self, thought_number: int, total_thoughts: int, next_thought_needed: bool) -> str:
        """Получает рекомендации"""
        if thought_number == 1:
            return "• Начните с постановки проблемы\n• Определите основные цели\n• Соберите необходимую информацию"
        elif thought_number < total_thoughts // 2:
            return "• Углубитесь в детали\n• Рассмотрите альтернативы\n• Проанализируйте риски"
        elif thought_number < total_thoughts:
            return "• Синтезируйте информацию\n• Принимайте решения\n• Планируйте действия"
        else:
            return "• Подведите итоги\n• Проверьте логику\n• Сформулируйте выводы"

    def get_next_steps(self, thought_number: int, total_thoughts: int, next_thought_needed: bool) -> str:
        """Получает следующие шаги"""
        if not next_thought_needed:
            return "🏁 Мышление завершено"
        
        if thought_number < total_thoughts:
            return f"➡️ Переходите к шагу {thought_number + 1}\n• Развивайте текущую мысль\n• Добавляйте новые аспекты\n• Углубляйте анализ"
        else:
            return "🔄 Рассмотрите дополнительные аспекты\n• Проверьте логику\n• Добавьте детали"

def main():
    """Главная функция для работы через STDIO"""
    server = SequentialThinkingSTDIOServer()
    
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