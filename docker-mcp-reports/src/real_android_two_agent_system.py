#!/usr/bin/env python3
"""
Real Android Two-Agent System - настоящая мультиагентная цепочка
Code Analyzer → Bug Detector
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from real_android_code_analyzer_agent import RealAndroidCodeAnalyzerAgent
from real_android_bug_detector_agent import RealAndroidBugDetectorAgent

logger = logging.getLogger(__name__)

class RealAndroidTwoAgentSystem:
    """Настоящая мультиагентная система из 2 агентов"""
    
    def __init__(self):
        # Создаем агентов
        self.code_analyzer = RealAndroidCodeAnalyzerAgent()
        self.bug_detector = RealAndroidBugDetectorAgent()
        
        # НАСТОЯЩАЯ ЦЕПОЧКА: связываем агентов
        self.code_analyzer.add_next_agent(self.bug_detector)
        
        # Настраиваем меж-агентное общение
        self.code_analyzer.other_agents['real_bug_detector'] = self.bug_detector
        self.bug_detector.other_agents['real_code_analyzer'] = self.code_analyzer
        
        logger.info("Настоящая мультиагентная система из 2 агентов инициализирована")
        logger.info(f"Цепочка: {self.code_analyzer.name} → {self.bug_detector.name}")
    
    async def process_android_project(self, project_path: str) -> Dict[str, Any]:
        """Обрабатывает Android проект через НАСТОЯЩУЮ цепочку агентов"""
        logger.info(f"Запуск настоящей мультиагентной цепочки для проекта: {project_path}")
        
        try:
            # Запускаем цепочку агентов - каждый принимает решения!
            result = await self.code_analyzer.process_chain(project_path)
            
            # Объединяем результаты
            final_result = {
                'project_path': project_path,
                'chain_result': result,
                'agent_decisions': self._extract_agent_decisions(),
                'inter_agent_communication': self._extract_communication_log(),
                'summary': self._create_summary(result),
                'processing_timestamp': asyncio.get_event_loop().time()
            }
            
            logger.info(f"Настоящая мультиагентная цепочка завершена для проекта: {project_path}")
            return final_result
            
        except Exception as e:
            logger.error(f"Ошибка в мультиагентной цепочке: {str(e)}")
            raise
    
    def _extract_agent_decisions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Извлекает решения, принятые агентами"""
        decisions = {}
        
        # Решения Code Analyzer
        if hasattr(self.code_analyzer, 'decision_history'):
            decisions['code_analyzer'] = self.code_analyzer.decision_history
        
        # Решения Bug Detector
        if hasattr(self.bug_detector, 'decision_history'):
            decisions['bug_detector'] = self.bug_detector.decision_history
        
        return decisions
    
    def _extract_communication_log(self) -> List[Dict[str, Any]]:
        """Извлекает лог меж-агентного общения"""
        communication_log = []
        
        # Логируем сообщения между агентами
        for agent in [self.code_analyzer, self.bug_detector]:
            if hasattr(agent, 'message_queue'):
                for message in agent.message_queue:
                    communication_log.append({
                        'from': message.sender,
                        'to': message.receiver,
                        'type': message.message_type,
                        'timestamp': message.timestamp
                    })
        
        return communication_log
    
    def _create_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Создает сводку по результатам мультиагентной обработки"""
        if isinstance(result, dict) and 'bugs' in result:
            # Результат от Bug Detector
            bugs = result.get('bugs', {})
            analysis = result.get('analysis', {})
            
            return {
                'overall_score': analysis.get('overall_score', 0),
                'total_bugs': bugs.get('total_bugs', 0),
                'critical_bugs': len(bugs.get('critical_bugs', [])),
                'high_priority_bugs': len(bugs.get('high_priority_bugs', [])),
                'scan_mode': bugs.get('scan_mode', 'standard'),
                'focus_areas': bugs.get('focus_areas', []),
                'agent_decisions_count': len(self._extract_agent_decisions().get('code_analyzer', [])) + 
                                       len(self._extract_agent_decisions().get('bug_detector', [])),
                'inter_agent_messages': len(self._extract_communication_log()),
                'project_health': self._assess_project_health(analysis.get('overall_score', 0))
            }
        else:
            # Результат от Code Analyzer (если Bug Detector не сработал)
            return {
                'overall_score': result.get('overall_score', 0),
                'analysis_mode': result.get('analysis_mode', 'standard'),
                'needs_bug_detection': result.get('needs_bug_detection', False),
                'bug_detection_priority': result.get('bug_detection_priority', 'normal'),
                'project_health': self._assess_project_health(result.get('overall_score', 0))
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
    
    async def get_agent_status(self) -> Dict[str, str]:
        """Получает статус агентов"""
        return {
            'code_analyzer': self.code_analyzer.status.value,
            'bug_detector': self.bug_detector.status.value
        }
    
    async def get_agent_chain_info(self) -> Dict[str, Any]:
        """Получает информацию о цепочке агентов"""
        return {
            'chain_length': 2,
            'agents': [
                {
                    'name': self.code_analyzer.name,
                    'status': self.code_analyzer.status.value,
                    'next_agents': [a.name for a in self.code_analyzer.next_agents],
                    'decisions_count': len(self.code_analyzer.decision_history)
                },
                {
                    'name': self.bug_detector.name,
                    'status': self.bug_detector.status.value,
                    'next_agents': [a.name for a in self.bug_detector.next_agents],
                    'decisions_count': len(self.bug_detector.decision_history)
                }
            ],
            'communication_log': self._extract_communication_log()
        }
    
    async def send_message_to_agent(self, agent_name: str, message_type: str, data: Any):
        """Отправляет сообщение конкретному агенту"""
        if agent_name == 'code_analyzer':
            self.code_analyzer.send_message('code_analyzer', message_type, data)
        elif agent_name == 'bug_detector':
            self.bug_detector.send_message('bug_detector', message_type, data)
        else:
            logger.error(f"Агент {agent_name} не найден")
    
    async def broadcast_message(self, message_type: str, data: Any):
        """Отправляет сообщение всем агентам"""
        self.code_analyzer.send_message('code_analyzer', message_type, data)
        self.bug_detector.send_message('bug_detector', message_type, data)
    
    async def process_message(self, message):
        """Обрабатывает сообщения"""
        if message.get('message_type') == "process_android_project":
            result = await self.process_android_project(message.get('data'))
            return result
        return None
