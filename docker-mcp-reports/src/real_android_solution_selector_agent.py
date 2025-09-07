import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import openai
from base_agent import BaseAgent, AgentMessage

logger = logging.getLogger(__name__)

class RealAndroidSolutionSelectorAgent(BaseAgent):
    """
    Четвертый агент в цепочке - выбирает лучшее решение из предложенных
    Использует реальную нейронную сеть (GPT-4) для анализа и выбора решений
    """
    
    def __init__(self, agent_id: str = "solution_selector"):
        super().__init__(agent_id)
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    async def select_best_solutions(self, solutions_data: List[Dict[str, Any]], project_context: str = "") -> Dict[str, Any]:
        """
        Выбирает лучшие решения из предложенных
        
        Args:
            solutions_data: Список решений от третьего агента
            project_context: Контекст проекта для лучшего понимания
            
        Returns:
            Словарь с выбранными лучшими решениями
        """
        try:
            logger.info(f"Выбираю лучшие решения из {len(solutions_data)} предложенных")
            
            # Формируем промпт для выбора решений
            prompt = self._build_solution_selection_prompt(solutions_data, project_context)
            
            # Вызываем GPT-4 для выбора решений
            response = await self._call_gpt4_for_selection(prompt)
            
            # Парсим ответ и структурируем выбранные решения
            selected_solutions = self._parse_selection_response(response, solutions_data)
            
            logger.info(f"Выбрано {len(selected_solutions)} лучших решений")
            return {
                "status": "success",
                "selected_solutions": selected_solutions,
                "total_proposed": len(solutions_data),
                "selected_count": len(selected_solutions)
            }
            
        except Exception as e:
            logger.error(f"Ошибка при выборе решений: {e}")
            return {
                "status": "error",
                "error": str(e),
                "selected_solutions": []
            }
    
    def _build_solution_selection_prompt(self, solutions_data: List[Dict[str, Any]], project_context: str) -> str:
        """Строит промпт для выбора лучших решений"""
        
        solutions_text = ""
        for i, solution in enumerate(solutions_data, 1):
            solutions_text += f"""
Решение #{i}:
- Баг: {solution.get('bug_file', 'unknown')} (индекс {solution.get('bug_index', 'unknown')})
- Название: {solution.get('title', 'No title')}
- Описание: {solution.get('description', 'No description')}
- Сложность: {solution.get('complexity', 'unknown')}
- Время: {solution.get('estimated_hours', 'unknown')} часов
- Приоритет: {solution.get('priority', 'unknown')}
- Шаги: {len(solution.get('steps', []))} шагов
- Код: {'Есть' if solution.get('code_example') else 'Нет'}
"""
        
        prompt = f"""Ты - эксперт по Android разработке на Kotlin. Твоя задача - выбрать лучшие решения из предложенных, учитывая:

1. Эффективность решения
2. Сложность реализации
3. Время на реализацию
4. Риски внедрения
5. Соответствие архитектуре проекта
6. Приоритет бага

КОНТЕКСТ ПРОЕКТА:
{project_context}

ПРЕДЛОЖЕННЫЕ РЕШЕНИЯ:
{solutions_text}

ЗАДАЧА:
Выбери ЛУЧШЕЕ решение для каждого бага, учитывая:
- Соотношение эффективность/сложность
- Минимальные риски
- Соответствие лучшим практикам Android
- Реалистичность в контексте проекта

ФОРМАТ ОТВЕТА (строго JSON):
{{
  "selected_solutions": [
    {{
      "bug_index": 1,
      "bug_file": "path/to/file.kt",
      "selected_solution": {{
        "title": "Название выбранного решения",
        "description": "Описание решения",
        "steps": ["шаг1", "шаг2", "шаг3"],
        "code_example": "// Код решения",
        "expected_result": "Ожидаемый результат",
        "complexity": "легко|средне|сложно",
        "estimated_hours": 2,
        "priority": "высокий|средний|низкий",
        "selection_reason": "Почему выбрано именно это решение",
        "implementation_order": 1,
        "risk_level": "низкий|средний|высокий"
      }},
      "alternative_solutions": [
        {{
          "title": "Альтернативное решение",
          "reason_not_selected": "Почему не выбрано"
        }}
      ]
    }}
  ],
  "implementation_plan": {{
    "total_hours": 10,
    "phases": [
      {{
        "phase": 1,
        "description": "Критические исправления",
        "solutions": [1, 2],
        "estimated_hours": 4
      }},
      {{
        "phase": 2,
        "description": "Улучшения",
        "solutions": [3, 4],
        "estimated_hours": 6
      }}
    ]
  }}
}}

ВАЖНО:
- Выбирай только РЕАЛИСТИЧНЫЕ решения
- Учитывай приоритеты и зависимости
- Предлагай план поэтапной реализации
- Оценивай риски каждого решения
"""
        
        return prompt
    
    async def _call_gpt4_for_selection(self, prompt: str) -> str:
        """Вызывает GPT-4 для выбора решений"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "Ты - эксперт по Android разработке на Kotlin. Выбираешь лучшие решения для багов в Android проектах, учитывая эффективность, сложность и риски."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Ошибка при вызове GPT-4: {e}")
            raise
    
    def _parse_selection_response(self, response: str, solutions_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Парсит ответ GPT-4 и структурирует выбранные решения"""
        try:
            # Пытаемся найти JSON в ответе
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("Не найден JSON в ответе GPT-4")
                return self._create_fallback_selection(solutions_data)
            
            json_str = response[start_idx:end_idx]
            data = json.loads(json_str)
            
            selected_solutions = []
            for selection in data.get('selected_solutions', []):
                bug_index = selection.get('bug_index', 1)
                bug_file = selection.get('bug_file', 'unknown')
                selected_solution = selection.get('selected_solution', {})
                alternative_solutions = selection.get('alternative_solutions', [])
                
                selected_solutions.append({
                    'bug_index': bug_index,
                    'bug_file': bug_file,
                    'selected_solution': {
                        'title': selected_solution.get('title', 'Выбранное решение'),
                        'description': selected_solution.get('description', 'Описание решения'),
                        'steps': selected_solution.get('steps', []),
                        'code_example': selected_solution.get('code_example', ''),
                        'expected_result': selected_solution.get('expected_result', ''),
                        'complexity': selected_solution.get('complexity', 'средне'),
                        'estimated_hours': selected_solution.get('estimated_hours', 1),
                        'priority': selected_solution.get('priority', 'средний'),
                        'selection_reason': selected_solution.get('selection_reason', 'Выбрано как лучшее решение'),
                        'implementation_order': selected_solution.get('implementation_order', 1),
                        'risk_level': selected_solution.get('risk_level', 'средний')
                    },
                    'alternative_solutions': alternative_solutions
                })
            
            # Добавляем план реализации если есть
            implementation_plan = data.get('implementation_plan', {})
            if implementation_plan:
                selected_solutions.append({
                    'implementation_plan': implementation_plan
                })
            
            return selected_solutions
            
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return self._create_fallback_selection(solutions_data)
        except Exception as e:
            logger.error(f"Ошибка при парсинге выбранных решений: {e}")
            return self._create_fallback_selection(solutions_data)
    
    def _create_fallback_selection(self, solutions_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Создает базовый выбор если парсинг не удался"""
        selected_solutions = []
        
        # Группируем решения по багам
        bugs_solutions = {}
        for solution in solutions_data:
            bug_index = solution.get('bug_index', 1)
            if bug_index not in bugs_solutions:
                bugs_solutions[bug_index] = []
            bugs_solutions[bug_index].append(solution)
        
        # Выбираем первое решение для каждого бага
        for bug_index, solutions in bugs_solutions.items():
            if solutions:
                first_solution = solutions[0]
                selected_solutions.append({
                    'bug_index': bug_index,
                    'bug_file': first_solution.get('bug_file', 'unknown'),
                    'selected_solution': {
                        'title': first_solution.get('title', 'Выбранное решение'),
                        'description': first_solution.get('description', 'Описание решения'),
                        'steps': first_solution.get('steps', []),
                        'code_example': first_solution.get('code_example', ''),
                        'expected_result': first_solution.get('expected_result', ''),
                        'complexity': first_solution.get('complexity', 'средне'),
                        'estimated_hours': first_solution.get('estimated_hours', 1),
                        'priority': first_solution.get('priority', 'средний'),
                        'selection_reason': 'Выбрано как первое доступное решение',
                        'implementation_order': bug_index,
                        'risk_level': 'средний'
                    },
                    'alternative_solutions': solutions[1:] if len(solutions) > 1 else []
                })
        
        return selected_solutions
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Основной метод обработки данных (требуется BaseAgent)"""
        logger.info(f"Агент {self.name} начинает выбор лучших решений")
        logger.info(f"Полученные данные от solution_generator:")
        logger.info(f"  - solutions: {data.get('solutions', [])}")
        logger.info(f"  - project_context: {data.get('project_context', '')}")
        
        try:
            # Просто отправляем решения нейронке для выбора лучших
            solutions_data = data.get('solutions', [])
            project_context = data.get('project_context', '')
            
            logger.info(f"Отправляю {len(solutions_data)} решений нейронке для выбора лучших")
            result = await self.select_best_solutions(solutions_data, project_context)
            return result
        except Exception as e:
            logger.error(f"Ошибка в process: {e}")
            return {
                "status": "error",
                "error": str(e),
                "selected_solutions": []
            }
    
    async def process_message(self, message: AgentMessage):
        """Обрабатывает сообщения от других агентов (требуется BaseAgent)"""
        try:
            if message.message_type == "solutions_generated":
                result = await self.process(message.data)
                self.send_message(message.sender, "best_solutions_selected", result)
            else:
                logger.warning(f"Неизвестный тип сообщения: {message.message_type}")
        except Exception as e:
            logger.error(f"Ошибка в process_message: {e}")

