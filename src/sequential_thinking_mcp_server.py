import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import sys

logger = logging.getLogger(__name__)

class SequentialThinkingMCPServer:
    """MCP сервер для последовательного мышления - аналог оригинального sequential thinking"""
    
    def __init__(self):
        self.thought_history: List[Dict[str, Any]] = []
        self.branches: Dict[str, List[Dict[str, Any]]] = {}
        self.disable_thought_logging = False  # Включаем логирование
        
        self.tools = {
            "sequential-thinking": {
                "name": "sequential-thinking",
                "description": """A detailed tool for dynamic and reflective problem-solving through thoughts.
This tool helps analyze problems through a flexible thinking process that can adapt and evolve.
Each thought can build on, question, or revise previous insights as understanding deepens.

When to use this tool:
- Breaking down complex problems into steps
- Planning and design with room for revision
- Analysis that might need course correction
- Problems where the full scope might not be clear initially
- Problems that require a multi-step solution
- Tasks that need to maintain context over multiple steps
- Situations where irrelevant information needs to be filtered out

Key features:
- You can adjust total_thoughts up or down as you progress
- You can question or revise previous thoughts
- You can add more thoughts even after reaching what seemed like the end
- You can express uncertainty and explore alternative approaches
- Not every thought needs to build linearly - you can branch or backtrack

Parameters explained:
- thought: Your current thinking step
- next_thought_needed: True if you need more thinking, even if at what seemed like the end
- thought_number: Current number in sequence (can go beyond initial total if needed)
- total_thoughts: Current estimate of thoughts needed (can be adjusted up/down)
- is_revision: A boolean indicating if this thought revises previous thinking
- revises_thought: If is_revision is true, which thought number is being reconsidered
- branch_from_thought: If branching, which thought number is the branching point
- branch_id: Identifier for the current branch (if any)
- needs_more_thoughts: If reaching end but realizing more thoughts needed

You should:
1. Start with an initial estimate of needed thoughts, but be ready to adjust
2. Feel free to question or revise previous thoughts
3. Don't hesitate to add more thoughts if needed, even at the "end"
4. Express uncertainty when present
5. Mark thoughts that revise previous thinking or branch into new paths
6. Only set next_thought_needed to false when truly done and a satisfactory answer is reached""",
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
                        },
                        "is_revision": {
                            "type": "boolean",
                            "description": "Whether this revises previous thinking"
                        },
                        "revises_thought": {
                            "type": "integer",
                            "description": "Which thought is being reconsidered",
                            "minimum": 1
                        },
                        "branch_from_thought": {
                            "type": "integer",
                            "description": "Branching point thought number",
                            "minimum": 1
                        },
                        "branch_id": {
                            "type": "string",
                            "description": "Branch identifier"
                        },
                        "needs_more_thoughts": {
                            "type": "boolean",
                            "description": "If more thoughts are needed"
                        }
                    },
                    "required": ["thought", "next_thought_needed", "thought_number", "total_thoughts"]
                }
            }
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Возвращает список доступных инструментов"""
        return list(self.tools.values())
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Выполняет вызов инструмента"""
        if tool_name not in self.tools:
            raise ValueError(f"Инструмент {tool_name} не найден")
        
        if tool_name == "sequential-thinking":
            return self._sequential_thinking(arguments)
        
        raise ValueError(f"Инструмент {tool_name} не реализован")
    
    def _validate_thought_data(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Валидация данных мысли"""
        thought = arguments.get("thought")
        if not thought or not isinstance(thought, str):
            raise ValueError("Invalid thought: must be a string")
        
        thought_number = arguments.get("thought_number")
        if not isinstance(thought_number, int) or thought_number < 1:
            raise ValueError("Invalid thought_number: must be a positive integer")
        
        total_thoughts = arguments.get("total_thoughts")
        if not isinstance(total_thoughts, int) or total_thoughts < 1:
            raise ValueError("Invalid total_thoughts: must be a positive integer")
        
        next_thought_needed = arguments.get("next_thought_needed")
        if not isinstance(next_thought_needed, bool):
            raise ValueError("Invalid next_thought_needed: must be a boolean")
        
        # Автоматически корректируем total_thoughts если нужно
        if thought_number > total_thoughts:
            total_thoughts = thought_number
        
        return {
            "thought": thought,
            "thought_number": thought_number,
            "total_thoughts": total_thoughts,
            "next_thought_needed": next_thought_needed,
            "is_revision": arguments.get("is_revision", False),
            "revises_thought": arguments.get("revises_thought"),
            "branch_from_thought": arguments.get("branch_from_thought"),
            "branch_id": arguments.get("branch_id"),
            "needs_more_thoughts": arguments.get("needs_more_thoughts", False)
        }
    
    def _format_thought(self, thought_data: Dict[str, Any]) -> str:
        """Форматирование мысли для вывода в stderr"""
        thought = thought_data["thought"]
        thought_number = thought_data["thought_number"]
        total_thoughts = thought_data["total_thoughts"]
        is_revision = thought_data.get("is_revision", False)
        revises_thought = thought_data.get("revises_thought")
        branch_from_thought = thought_data.get("branch_from_thought")
        branch_id = thought_data.get("branch_id")
        
        # Формируем префикс и контекст
        if is_revision:
            prefix = "🔄 Revision"
            context = f" (revising thought {revises_thought})" if revises_thought else ""
        elif branch_from_thought:
            prefix = "🌿 Branch"
            context = f" (from thought {branch_from_thought}, ID: {branch_id})" if branch_id else f" (from thought {branch_from_thought})"
        else:
            prefix = "💭 Thought"
            context = ""
        
        header = f"{prefix} {thought_number}/{total_thoughts}{context}"
        max_width = max(len(header), len(thought)) + 4
        border = "─" * max_width
        
        return f"""
┌{border}┐
│ {header:<{max_width-2}} │
├{border}┤
│ {thought:<{max_width-2}} │
└{border}┘"""
    
    def _sequential_thinking(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Обрабатывает вызов sequential thinking - аналог оригинального"""
        try:
            # Валидируем входные данные
            validated_input = self._validate_thought_data(arguments)
            
            # Добавляем в историю
            self.thought_history.append(validated_input)
            
            # Если это ветка, добавляем в соответствующую ветку
            if validated_input.get("branch_from_thought") and validated_input.get("branch_id"):
                branch_id = validated_input["branch_id"]
                if branch_id not in self.branches:
                    self.branches[branch_id] = []
                self.branches[branch_id].append(validated_input)
            
            # Логируем в stderr (как в оригинале)
            if not self.disable_thought_logging:
                formatted_thought = self._format_thought(validated_input)
                print(formatted_thought, file=sys.stderr)
                sys.stderr.flush()
            
            # Возвращаем JSON-ответ с состоянием (как в оригинале)
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "thought_number": validated_input["thought_number"],
                        "total_thoughts": validated_input["total_thoughts"],
                        "next_thought_needed": validated_input["next_thought_needed"],
                        "branches": list(self.branches.keys()),
                        "thought_history_length": len(self.thought_history)
                    }, indent=2)
                }]
            }
            
        except Exception as error:
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "error": str(error),
                        "status": "failed"
                    }, indent=2)
                }],
                "isError": True
            }