import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import openai
from base_agent import BaseAgent, AgentMessage

logger = logging.getLogger(__name__)

class RealAndroidSolutionGeneratorAgent(BaseAgent):
    """
    Третий агент в цепочке - генерирует решения на основе найденных багов
    Использует реальную нейронную сеть (GPT-4) для генерации решений
    """
    
    def __init__(self, agent_id: str = "solution_generator"):
        super().__init__(agent_id)
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    async def generate_solutions(self, bugs_data: List[Dict[str, Any]], project_context: str = "") -> Dict[str, Any]:
        """
        Генерирует решения для найденных багов
        
        Args:
            bugs_data: Список найденных багов от второго агента
            project_context: Контекст проекта для лучшего понимания
            
        Returns:
            Словарь с решениями для каждого бага
        """
        try:
            logger.info(f"Генерирую решения для {len(bugs_data)} багов")
            
            # Формируем промпт для генерации решений
            prompt = self._build_solution_generation_prompt(bugs_data, project_context)
            
            # Вызываем GPT-4 для генерации решений
            response = await self._call_gpt4_for_solutions(prompt)
            
            # Парсим ответ и структурируем решения
            solutions = self._parse_solutions_response(response, bugs_data)
            
            logger.info(f"Сгенерировано {len(solutions)} решений")
            return {
                "status": "success",
                "solutions": solutions,
                "total_bugs": len(bugs_data),
                "solutions_generated": len(solutions)
            }
            
        except Exception as e:
            logger.error(f"Ошибка при генерации решений: {e}")
            return {
                "status": "error",
                "error": str(e),
                "solutions": []
            }
    
    def _build_solution_generation_prompt(self, bugs_data: List[Dict[str, Any]], project_context: str) -> str:
        """Строит промпт для генерации решений"""
        
        bugs_text = ""
        for i, bug in enumerate(bugs_data, 1):
            bugs_text += f"""
Баг #{i}:
- Файл: {bug.get('file', 'unknown')}
- Описание: {bug.get('description', 'No description')}
- Строка: {bug.get('line', 'unknown')}
- Тип: {bug.get('type', 'unknown')}
- Критичность: {bug.get('severity', 'unknown')}
"""
        
        prompt = f"""Ты - эксперт по Android разработке на Kotlin. Твоя задача - сгенерировать конкретные, практические решения для найденных багов в Android проекте.

КОНТЕКСТ ПРОЕКТА:
{project_context}

НАЙДЕННЫЕ БАГИ:
{bugs_text}

ЗАДАЧА:
Для каждого бага сгенерируй 2-3 конкретных решения с указанием:
1. Краткое описание решения
2. Пошаговые действия для исправления
3. Код-примеры (если применимо)
4. Ожидаемый результат
5. Сложность реализации (легко/средне/сложно)
6. Время на реализацию (в часах)

ФОРМАТ ОТВЕТА (строго JSON):
{{
  "solutions": [
    {{
      "bug_index": 1,
      "bug_file": "path/to/file.kt",
      "solutions": [
        {{
          "title": "Краткое название решения",
          "description": "Подробное описание решения",
          "steps": [
            "Шаг 1: ...",
            "Шаг 2: ...",
            "Шаг 3: ..."
          ],
          "code_example": "// Пример кода для исправления",
          "expected_result": "Что должно получиться",
          "complexity": "легко|средне|сложно",
          "estimated_hours": 2,
          "priority": "высокий|средний|низкий"
        }}
      ]
    }}
  ]
}}

ВАЖНО:
- Будь конкретным и практичным
- Предлагай реальные решения, которые можно реализовать
- Учитывай архитектуру Android и лучшие практики
- Код должен быть на Kotlin
- Решения должны быть приоритизированы по важности
"""
        
        return prompt
    
    async def _call_gpt4_for_solutions(self, prompt: str) -> str:
        """Вызывает GPT-4 для генерации решений"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "Ты - эксперт по Android разработке на Kotlin. Генерируешь практические решения для багов в Android проектах."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Ошибка при вызове GPT-4: {e}")
            raise
    
    def _parse_solutions_response(self, response: str, bugs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Парсит ответ GPT-4 и структурирует решения"""
        try:
            # Пытаемся найти JSON в ответе
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("Не найден JSON в ответе GPT-4")
                return self._create_fallback_solutions(bugs_data)
            
            json_str = response[start_idx:end_idx]
            data = json.loads(json_str)
            
            solutions = []
            for solution_group in data.get('solutions', []):
                bug_index = solution_group.get('bug_index', 1)
                bug_file = solution_group.get('bug_file', 'unknown')
                bug_solutions = solution_group.get('solutions', [])
                
                for solution in bug_solutions:
                    solutions.append({
                        'bug_index': bug_index,
                        'bug_file': bug_file,
                        'title': solution.get('title', 'Решение'),
                        'description': solution.get('description', 'Описание решения'),
                        'steps': solution.get('steps', []),
                        'code_example': solution.get('code_example', ''),
                        'expected_result': solution.get('expected_result', ''),
                        'complexity': solution.get('complexity', 'средне'),
                        'estimated_hours': solution.get('estimated_hours', 1),
                        'priority': solution.get('priority', 'средний')
                    })
            
            return solutions
            
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return self._create_fallback_solutions(bugs_data)
        except Exception as e:
            logger.error(f"Ошибка при парсинге решений: {e}")
            return self._create_fallback_solutions(bugs_data)
    
    def _create_fallback_solutions(self, bugs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Создает базовые решения если парсинг не удался"""
        solutions = []
        for i, bug in enumerate(bugs_data, 1):
            solutions.append({
                'bug_index': i,
                'bug_file': bug.get('file', 'unknown'),
                'title': 'Базовое решение',
                'description': f'Исправить проблему в файле {bug.get("file", "unknown")}',
                'steps': [
                    'Проанализировать код в указанном файле',
                    'Найти причину проблемы',
                    'Применить соответствующее исправление'
                ],
                'code_example': '// Требуется анализ кода',
                'expected_result': 'Исправление найденной проблемы',
                'complexity': 'средне',
                'estimated_hours': 2,
                'priority': 'средний'
            })
        return solutions
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Основной метод обработки данных (требуется BaseAgent)"""
        logger.info(f"Агент {self.name} начинает генерацию решений")
        logger.info(f"Полученные данные от bug_detector:")
        logger.info(f"  - bugs: {data.get('bugs', {})}")
        logger.info(f"  - project_context: {data.get('project_context', '')}")
        
        try:
            # Просто отправляем баги нейронке для генерации решений
            bugs_data = data.get('all_bugs', [])
            project_context = data.get('project_context', '')
            
            logger.info(f"Отправляю {len(bugs_data)} багов нейронке для генерации решений")
            result = await self.generate_solutions(bugs_data, project_context)
            return result
        except Exception as e:
            logger.error(f"Ошибка в process: {e}")
            return {
                "status": "error",
                "error": str(e),
                "solutions": []
            }
    
    async def process_message(self, message: AgentMessage):
        """Обрабатывает сообщения от других агентов (требуется BaseAgent)"""
        try:
            if message.message_type == "bugs_found":
                result = await self.process(message.data)
                self.send_message(message.sender, "solutions_generated", result)
            else:
                logger.warning(f"Неизвестный тип сообщения: {message.message_type}")
        except Exception as e:
            logger.error(f"Ошибка в process_message: {e}")

