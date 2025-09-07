#!/usr/bin/env python3
"""
Real Android Four-Agent System - настоящая мультиагентная цепочка
Code Analyzer → Bug Detector → Solution Generator → Solution Selector
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from real_android_code_analyzer_agent import RealAndroidCodeAnalyzerAgent
from real_android_bug_detector_agent import RealAndroidBugDetectorAgent
from real_android_solution_generator_agent import RealAndroidSolutionGeneratorAgent
from real_android_solution_selector_agent import RealAndroidSolutionSelectorAgent

logger = logging.getLogger(__name__)

class RealAndroidFourAgentSystem:
    """Настоящая мультиагентная система из 4 агентов"""
    
    def __init__(self):
        # Создаем агентов
        self.code_analyzer = RealAndroidCodeAnalyzerAgent()
        self.bug_detector = RealAndroidBugDetectorAgent()
        self.solution_generator = RealAndroidSolutionGeneratorAgent()
        self.solution_selector = RealAndroidSolutionSelectorAgent()
        
        # НАСТОЯЩАЯ ЦЕПОЧКА: связываем агентов
        self.code_analyzer.add_next_agent(self.bug_detector)
        self.bug_detector.add_next_agent(self.solution_generator)
        self.solution_generator.add_next_agent(self.solution_selector)
        
        # Настраиваем меж-агентное общение
        self.code_analyzer.other_agents['real_bug_detector'] = self.bug_detector
        self.code_analyzer.other_agents['real_solution_generator'] = self.solution_generator
        self.code_analyzer.other_agents['real_solution_selector'] = self.solution_selector
        
        self.bug_detector.other_agents['real_code_analyzer'] = self.code_analyzer
        self.bug_detector.other_agents['real_solution_generator'] = self.solution_generator
        self.bug_detector.other_agents['real_solution_selector'] = self.solution_selector
        
        self.solution_generator.other_agents['real_code_analyzer'] = self.code_analyzer
        self.solution_generator.other_agents['real_bug_detector'] = self.bug_detector
        self.solution_generator.other_agents['real_solution_selector'] = self.solution_selector
        
        self.solution_selector.other_agents['real_code_analyzer'] = self.code_analyzer
        self.solution_selector.other_agents['real_bug_detector'] = self.bug_detector
        self.solution_selector.other_agents['real_solution_generator'] = self.solution_generator
        
        logger.info("Настоящая мультиагентная система из 4 агентов инициализирована")
        logger.info(f"Цепочка: {self.code_analyzer.name} → {self.bug_detector.name} → {self.solution_generator.name} → {self.solution_selector.name}")
    
    async def process_android_project(self, project_path: str) -> Dict[str, Any]:
        """Обрабатывает Android проект через НАСТОЯЩУЮ цепочку из 4 агентов"""
        logger.info(f"Запуск настоящей мультиагентной цепочки из 4 агентов для проекта: {project_path}")
        
        try:
            # Этап 1: Анализ кода
            logger.info("Этап 1: Анализ кода...")
            analysis_result = await self.code_analyzer.process(project_path)
            
            # Этап 2: Поиск багов
            logger.info("Этап 2: Поиск багов...")
            logger.info(f"Передаю данные от code_analyzer к bug_detector:")
            logger.info(f"  - project_structure: {len(analysis_result.get('project_structure', {}))} категорий")
            logger.info(f"  - file_contents: {len(analysis_result.get('file_contents', {}))} файлов")
            logger.info(f"  - architecture_analysis: {analysis_result.get('architecture_analysis', {})}")
            logger.info(f"  - file_analysis: {analysis_result.get('file_analysis', {})}")
            
            # Передаем ВСЕ данные от code_analyzer в bug_detector
            bugs_data = {
                'project_path': project_path,
                'project_structure': analysis_result.get('project_structure', {}),
                'architecture_analysis': analysis_result.get('architecture_analysis', {}),
                'file_analysis': analysis_result.get('file_analysis', {}),
                'file_contents': analysis_result.get('file_contents', {}),  # Добавляем содержимое файлов
                'overall_score': analysis_result.get('overall_score', 0),
                'analysis_result': analysis_result,
                # Добавляем найденные проблемы от code_analyzer
                'complexity_issues': analysis_result.get('file_analysis', {}).get('complexity_issues', []),
                'architecture_issues': analysis_result.get('architecture_analysis', {}).get('issues', [])
            }
            bugs_result = await self.bug_detector.process(bugs_data)
            
            # Этап 3: Генерация решений
            logger.info("Этап 3: Генерация решений...")
            logger.info(f"Передаю данные от bug_detector к solution_generator:")
            logger.info(f"  - bugs: {bugs_result.get('total_bugs', 0)} багов")
            logger.info(f"  - critical_bugs: {len(bugs_result.get('critical_bugs', []))}")
            
            solutions_data = {
                'bugs': bugs_result,
                'project_context': analysis_result.get('summary', '')
            }
            solutions_result = await self.solution_generator.process(solutions_data)
            
            # Этап 4: Выбор лучших решений
            logger.info("Этап 4: Выбор лучших решений...")
            logger.info(f"Передаю данные от solution_generator к solution_selector:")
            logger.info(f"  - solutions: {len(solutions_result.get('solutions', []))} решений")
            
            selection_data = {
                'solutions': solutions_result.get('solutions', []),
                'project_context': analysis_result.get('summary', '')
            }
            selection_result = await self.solution_selector.process(selection_data)
            
            # Объединяем результаты всех этапов
            final_result = {
                'project_path': project_path,
                'analysis': analysis_result,
                'bugs': bugs_result,
                'solutions': solutions_result,
                'selected_solutions': selection_result,
                'agent_decisions': self._extract_agent_decisions(),
                'inter_agent_communication': self._extract_communication_log(),
                'summary': self._create_comprehensive_summary(analysis_result, bugs_result, solutions_result, selection_result),
                'processing_timestamp': asyncio.get_event_loop().time()
            }
            
            logger.info(f"Настоящая мультиагентная цепочка из 4 агентов завершена для проекта: {project_path}")
            return final_result
            
        except Exception as e:
            logger.error(f"Ошибка в мультиагентной цепочке из 4 агентов: {str(e)}")
            raise
    
    def _extract_agent_decisions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Извлекает решения, принятые агентами"""
        decisions = {}
        
        # Решения всех агентов
        agents = [
            ('code_analyzer', self.code_analyzer),
            ('bug_detector', self.bug_detector),
            ('solution_generator', self.solution_generator),
            ('solution_selector', self.solution_selector)
        ]
        
        for agent_name, agent in agents:
            if hasattr(agent, 'decision_history'):
                decisions[agent_name] = agent.decision_history
        
        return decisions
    
    def _extract_communication_log(self) -> List[Dict[str, Any]]:
        """Извлекает лог меж-агентного общения"""
        communication_log = []
        
        # Логируем сообщения между агентами
        agents = [self.code_analyzer, self.bug_detector, self.solution_generator, self.solution_selector]
        for agent in agents:
            if hasattr(agent, 'message_queue'):
                for message in agent.message_queue:
                    communication_log.append({
                        'from': message.sender,
                        'to': message.receiver,
                        'type': message.message_type,
                        'timestamp': message.timestamp
                    })
        
        return communication_log
    
    def _create_comprehensive_summary(self, analysis_result: Dict[str, Any], bugs_result: Dict[str, Any], 
                                    solutions_result: Dict[str, Any], selection_result: Dict[str, Any]) -> Dict[str, Any]:
        """Создает комплексную сводку по результатам всех 4 агентов"""
        
        # Анализ кода
        analysis_summary = analysis_result.get('summary', {})
        overall_score = analysis_summary.get('overall_score', 0)
        
        # Баги
        bugs_data = bugs_result.get('bugs', {})
        total_bugs = bugs_data.get('total_bugs', 0)
        critical_bugs = len(bugs_data.get('critical_bugs', []))
        high_priority_bugs = len(bugs_data.get('high_priority_bugs', []))
        
        # Решения
        solutions_data = solutions_result.get('solutions', [])
        total_solutions = len(solutions_data)
        
        # Выбранные решения
        selected_solutions = selection_result.get('selected_solutions', [])
        selected_count = len([s for s in selected_solutions if 'selected_solution' in s])
        
        # План реализации
        implementation_plan = None
        for solution in selected_solutions:
            if 'implementation_plan' in solution:
                implementation_plan = solution['implementation_plan']
                break
        
        return {
            'overall_score': overall_score,
            'total_bugs': total_bugs,
            'critical_bugs': critical_bugs,
            'high_priority_bugs': high_priority_bugs,
            'total_solutions_generated': total_solutions,
            'selected_solutions_count': selected_count,
            'implementation_plan': implementation_plan,
            'agent_decisions_count': sum(len(decisions) for decisions in self._extract_agent_decisions().values()),
            'inter_agent_messages': len(self._extract_communication_log()),
            'project_health': self._assess_project_health(overall_score),
            'recommendations': self._generate_recommendations(total_bugs, selected_count, overall_score)
        }
    
    def _assess_project_health(self, overall_score: float) -> str:
        """Оценивает общее состояние проекта"""
        if overall_score >= 0.8:
            return 'excellent'
        elif overall_score >= 0.6:
            return 'good'
        elif overall_score >= 0.4:
            return 'fair'
        else:
            return 'poor'
    
    def _generate_recommendations(self, total_bugs: int, selected_solutions: int, overall_score: float) -> List[str]:
        """Генерирует рекомендации на основе анализа"""
        recommendations = []
        
        if total_bugs == 0:
            recommendations.append("Проект не содержит критических багов - отличная работа!")
        elif total_bugs <= 3:
            recommendations.append("Небольшое количество багов - рекомендуется исправить в ближайшее время")
        else:
            recommendations.append("Обнаружено значительное количество багов - требуется срочное исправление")
        
        if selected_solutions > 0:
            recommendations.append(f"Подготовлено {selected_solutions} решений для исправления багов")
        
        if overall_score < 0.5:
            recommendations.append("Рекомендуется провести рефакторинг кода для улучшения качества")
        elif overall_score < 0.7:
            recommendations.append("Код в хорошем состоянии, но есть возможности для улучшения")
        else:
            recommendations.append("Код высокого качества - продолжайте поддерживать стандарты")
        
        return recommendations
    
    async def get_agent_status(self) -> Dict[str, str]:
        """Получает статус агентов"""
        return {
            'code_analyzer': self.code_analyzer.status.value,
            'bug_detector': self.bug_detector.status.value,
            'solution_generator': self.solution_generator.status.value,
            'solution_selector': self.solution_selector.status.value
        }
    
    async def get_agent_chain_info(self) -> Dict[str, Any]:
        """Получает информацию о цепочке агентов"""
        agents = [
            ('code_analyzer', self.code_analyzer),
            ('bug_detector', self.bug_detector),
            ('solution_generator', self.solution_generator),
            ('solution_selector', self.solution_selector)
        ]
        
        return {
            'chain_length': 4,
            'agents': [
                {
                    'name': agent.name,
                    'status': agent.status.value,
                    'next_agents': [a.name for a in agent.next_agents],
                    'decisions_count': len(agent.decision_history)
                }
                for _, agent in agents
            ],
            'communication_log': self._extract_communication_log()
        }
    
    async def send_message_to_agent(self, agent_name: str, message_type: str, data: Any):
        """Отправляет сообщение конкретному агенту"""
        agent_map = {
            'code_analyzer': self.code_analyzer,
            'bug_detector': self.bug_detector,
            'solution_generator': self.solution_generator,
            'solution_selector': self.solution_selector
        }
        
        if agent_name in agent_map:
            agent_map[agent_name].send_message(agent_name, message_type, data)
        else:
            logger.error(f"Агент {agent_name} не найден")
    
    async def broadcast_message(self, message_type: str, data: Any):
        """Отправляет сообщение всем агентам"""
        agents = [self.code_analyzer, self.bug_detector, self.solution_generator, self.solution_selector]
        for agent in agents:
            agent.send_message(agent.name, message_type, data)
    
    async def process_message(self, message):
        """Обрабатывает сообщения"""
        if message.get('message_type') == "process_android_project":
            result = await self.process_android_project(message.get('data'))
            return result
        return None