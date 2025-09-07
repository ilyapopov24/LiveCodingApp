#!/usr/bin/env python3
"""
Real Android Bug Detector Agent - настоящий агент с принятием решений
"""

import asyncio
import logging
import os
import re
import json
from typing import Any, Dict, List, Optional
from pathlib import Path
from base_agent import BaseAgent, AgentMessage
import openai

logger = logging.getLogger(__name__)

class RealAndroidBugDetectorAgent(BaseAgent):
    """Настоящий агент для поиска багов с принятием решений"""
    
    def __init__(self):
        super().__init__("real_bug_detector")
        self.bug_patterns = self._load_bug_patterns()
        self.severity_levels = ['critical', 'high', 'medium', 'low']
        self.scan_mode = 'standard'  # standard, focused, aggressive
        self.focus_areas = ['critical_bugs']
        self.max_bugs_threshold = 50
        self.decision_history = []
        
        # Инициализируем OpenAI клиент
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY не установлен")
        self.openai_client = openai.OpenAI(api_key=api_key)
        
        logger.info(f"Настоящий агент {self.name} инициализирован")
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ищет баги с принятием решений"""
        logger.info(f"Агент {self.name} начинает поиск багов")
        
        try:
            # ПРИНИМАЕМ РЕШЕНИЕ: какой режим поиска использовать?
            scan_mode = data.get('scan_mode', 'standard')
            focus_areas = data.get('focus_areas', ['critical_bugs'])
            
            self.scan_mode = scan_mode
            self.focus_areas = focus_areas
            
            logger.info(f"Агент {self.name} выбрал режим поиска: {scan_mode}, области: {focus_areas}")
            
            # ПРИНИМАЕМ РЕШЕНИЕ: нужно ли адаптировать поиск?
            adapted_focus = self._adapt_focus_areas(data)
            
            # Выполняем поиск багов
            bugs = await self._perform_bug_scan(data, adapted_focus)
            
            # ПРИНИМАЕМ РЕШЕНИЕ: как классифицировать найденные баги?
            classified_bugs = await self._classify_bugs_intelligently(bugs, data)
            
            # ПРИНИМАЕМ РЕШЕНИЕ: нужно ли уведомить предыдущего агента?
            if len(classified_bugs) > 10:
                self._notify_previous_agent_about_bugs(classified_bugs)
            
            result = {
                'project_path': data.get('project_path'),
                'total_bugs': len(classified_bugs),
                'bugs_by_severity': self._group_bugs_by_severity(classified_bugs),
                'bugs_by_category': self._group_bugs_by_category(classified_bugs),
                'critical_bugs': [b for b in classified_bugs if b['severity'] == 'critical'],
                'high_priority_bugs': [b for b in classified_bugs if b['severity'] in ['critical', 'high']],
                'all_bugs': classified_bugs,
                'scan_mode': scan_mode,
                'focus_areas': adapted_focus,
                'detection_timestamp': asyncio.get_event_loop().time()
            }
            
            # Записываем решение в историю
            self.decision_history.append({
                'timestamp': asyncio.get_event_loop().time(),
                'decision': 'scan_mode',
                'value': scan_mode,
                'reasoning': f"Выбран режим {scan_mode} на основе данных от Code Analyzer"
            })
            
            logger.info(f"Агент {self.name} завершил поиск багов. Найдено: {len(classified_bugs)} багов")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка в агенте {self.name}: {str(e)}")
            raise
    
    def _adapt_focus_areas(self, data: Dict[str, Any]) -> List[str]:
        """ПРИНИМАЕТ РЕШЕНИЕ: адаптирует области поиска на основе анализа"""
        focus_areas = data.get('focus_areas', ['critical_bugs'])
        architecture_analysis = data.get('architecture_analysis', {})
        file_analysis = data.get('file_analysis', {})
        
        adapted_focus = focus_areas.copy()
        
        # Агент решает, какие области добавить на основе анализа
        if not architecture_analysis.get('has_mvvm', False):
            adapted_focus.append('architecture_issues')
            logger.info("Агент добавил поиск архитектурных проблем - MVVM не найден")
        
        if file_analysis.get('complexity_issues'):
            adapted_focus.append('performance_issues')
            logger.info("Агент добавил поиск проблем производительности - найдены проблемы сложности")
        
        if data.get('overall_score', 0) < 0.5:
            adapted_focus.append('security_issues')
            logger.info("Агент добавил поиск проблем безопасности - низкая оценка проекта")
        
        return adapted_focus
    
    async def _perform_bug_scan(self, data: Dict[str, Any], focus_areas: List[str]) -> List[Dict[str, Any]]:
        """Выполняет поиск багов в выбранных областях с помощью нейронки"""
        logger.info(f"Запускаю нейронный поиск багов в областях: {focus_areas}")
        return await self._perform_neural_bug_scan(data, focus_areas)
    
    async def _scan_critical_bugs(self, project_path: str, project_structure: Dict) -> List[Dict[str, Any]]:
        """Ищет критические баги"""
        bugs = []
        
        # Сканируем все Kotlin/Java файлы
        for category, files in project_structure.items():
            if isinstance(files, list):
                for file_path in files:
                    if file_path.endswith(('.kt', '.java')):
                        full_path = os.path.join(project_path, file_path)
                        file_bugs = await self._analyze_file_for_critical_bugs(full_path, file_path)
                        bugs.extend(file_bugs)
        
        return bugs
    
    async def _analyze_file_for_critical_bugs(self, full_path: str, relative_path: str) -> List[Dict[str, Any]]:
        """Анализирует файл на критические баги"""
        bugs = []
        
        try:
            if not os.path.exists(full_path):
                return bugs
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Проверяем на критические Android баги
            if 'Activity' in relative_path or 'Fragment' in relative_path:
                # Проверяем на отсутствие super.onCreate()
                if 'onCreate' in content and 'super.onCreate' not in content:
                    bugs.append({
                        'type': 'critical_lifecycle',
                        'severity': 'critical',
                        'category': 'android',
                        'file': relative_path,
                        'line': self._find_line_number(content, 'onCreate'),
                        'description': 'Отсутствует вызов super.onCreate() - критическая ошибка',
                        'suggestion': 'Добавьте super.onCreate(savedInstanceState) в начало метода onCreate()'
                    })
                
                # Проверяем на утечки памяти
                if 'static' in content and 'Context' in content:
                    bugs.append({
                        'type': 'memory_leak',
                        'severity': 'high',
                        'category': 'android',
                        'file': relative_path,
                        'line': self._find_line_number(content, 'static.*Context'),
                        'description': 'Возможная утечка памяти: статическая ссылка на Context',
                        'suggestion': 'Используйте Application Context или WeakReference'
                    })
            
            # Проверяем на критические проблемы с null
            if '!!' in content:
                bugs.append({
                    'type': 'null_pointer_risk',
                    'severity': 'high',
                    'category': 'general',
                    'file': relative_path,
                    'line': self._find_line_number(content, '!!'),
                    'description': 'Использование оператора !! может привести к NPE',
                    'suggestion': 'Используйте безопасные вызовы ?. или проверки на null'
                })
            
        except Exception as e:
            logger.warning(f"Ошибка при анализе файла {full_path}: {str(e)}")
        
        return bugs
    
    async def _scan_memory_leaks(self, project_path: str, project_structure: Dict) -> List[Dict[str, Any]]:
        """Ищет утечки памяти"""
        bugs = []
        
        for category, files in project_structure.items():
            if isinstance(files, list):
                for file_path in files:
                    if file_path.endswith(('.kt', '.java')):
                        full_path = os.path.join(project_path, file_path)
                        file_bugs = await self._analyze_file_for_memory_leaks(full_path, file_path)
                        bugs.extend(file_bugs)
        
        return bugs
    
    async def _analyze_file_for_memory_leaks(self, full_path: str, relative_path: str) -> List[Dict[str, Any]]:
        """Анализирует файл на утечки памяти"""
        bugs = []
        
        try:
            if not os.path.exists(full_path):
                return bugs
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем на статические ссылки на Context
            if re.search(r'static.*Context', content):
                bugs.append({
                    'type': 'memory_leak',
                    'severity': 'high',
                    'category': 'memory',
                    'file': relative_path,
                    'line': self._find_line_number(content, 'static.*Context'),
                    'description': 'Статическая ссылка на Context может вызвать утечку памяти',
                    'suggestion': 'Используйте Application Context или WeakReference'
                })
            
            # Проверяем на неосвобожденные ресурсы
            if 'FileInputStream' in content and 'close()' not in content:
                bugs.append({
                    'type': 'resource_leak',
                    'severity': 'medium',
                    'category': 'memory',
                    'file': relative_path,
                    'line': self._find_line_number(content, 'FileInputStream'),
                    'description': 'FileInputStream не закрывается - возможна утечка ресурсов',
                    'suggestion': 'Используйте try-with-resources или явно закрывайте поток'
                })
            
        except Exception as e:
            logger.warning(f"Ошибка при анализе утечек памяти в {full_path}: {str(e)}")
        
        return bugs
    
    async def _scan_performance_issues(self, project_path: str, project_structure: Dict) -> List[Dict[str, Any]]:
        """Ищет проблемы с производительностью"""
        bugs = []
        
        for category, files in project_structure.items():
            if isinstance(files, list):
                for file_path in files:
                    if file_path.endswith(('.kt', '.java')):
                        full_path = os.path.join(project_path, file_path)
                        file_bugs = await self._analyze_file_for_performance(full_path, file_path)
                        bugs.extend(file_bugs)
        
        return bugs
    
    async def _analyze_file_for_performance(self, full_path: str, relative_path: str) -> List[Dict[str, Any]]:
        """Анализирует файл на проблемы производительности"""
        bugs = []
        
        try:
            if not os.path.exists(full_path):
                return bugs
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем на findViewById в цикле
            if 'findViewById' in content and ('for' in content or 'while' in content):
                bugs.append({
                    'type': 'performance_issue',
                    'severity': 'high',
                    'category': 'performance',
                    'file': relative_path,
                    'line': self._find_line_number(content, 'findViewById'),
                    'description': 'findViewById в цикле может замедлить работу',
                    'suggestion': 'Кэшируйте View или используйте ViewBinding'
                })
            
            # Проверяем на создание объектов в цикле
            if 'new ' in content and ('for' in content or 'while' in content):
                bugs.append({
                    'type': 'performance_issue',
                    'severity': 'medium',
                    'category': 'performance',
                    'file': relative_path,
                    'line': 0,
                    'description': 'Создание объектов в цикле',
                    'suggestion': 'Вынесите создание объектов за пределы цикла'
                })
            
        except Exception as e:
            logger.warning(f"Ошибка при анализе производительности в {full_path}: {str(e)}")
        
        return bugs
    
    async def _scan_security_issues(self, project_path: str, project_structure: Dict) -> List[Dict[str, Any]]:
        """Ищет проблемы с безопасностью"""
        bugs = []
        
        for category, files in project_structure.items():
            if isinstance(files, list):
                for file_path in files:
                    if file_path.endswith(('.kt', '.java')):
                        full_path = os.path.join(project_path, file_path)
                        file_bugs = await self._analyze_file_for_security(full_path, file_path)
                        bugs.extend(file_bugs)
        
        return bugs
    
    async def _analyze_file_for_security(self, full_path: str, relative_path: str) -> List[Dict[str, Any]]:
        """Анализирует файл на проблемы безопасности"""
        bugs = []
        
        try:
            if not os.path.exists(full_path):
                return bugs
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем на хардкод паролей
            if re.search(r'password\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
                bugs.append({
                    'type': 'security_issue',
                    'severity': 'critical',
                    'category': 'security',
                    'file': relative_path,
                    'line': self._find_line_number(content, 'password'),
                    'description': 'Хардкод пароля в коде',
                    'suggestion': 'Используйте SecurePreferences или KeyStore'
                })
            
            # Проверяем на логирование чувствительных данных
            if 'Log.' in content and ('password' in content or 'token' in content or 'key' in content):
                bugs.append({
                    'type': 'security_issue',
                    'severity': 'high',
                    'category': 'security',
                    'file': relative_path,
                    'line': self._find_line_number(content, 'Log.'),
                    'description': 'Логирование чувствительных данных',
                    'suggestion': 'Не логируйте пароли, токены и ключи'
                })
            
        except Exception as e:
            logger.warning(f"Ошибка при анализе безопасности в {full_path}: {str(e)}")
        
        return bugs
    
    async def _scan_architecture_issues(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ищет архитектурные проблемы"""
        bugs = []
        architecture_analysis = data.get('architecture_analysis', {})
        
        if not architecture_analysis.get('has_mvvm', False):
            bugs.append({
                'type': 'architecture_issue',
                'severity': 'medium',
                'category': 'architecture',
                'file': 'project',
                'line': 0,
                'description': 'Отсутствует MVVM архитектура',
                'suggestion': 'Реализуйте MVVM с ViewModel и LiveData'
            })
        
        if not architecture_analysis.get('has_clean_architecture', False):
            bugs.append({
                'type': 'architecture_issue',
                'severity': 'low',
                'category': 'architecture',
                'file': 'project',
                'line': 0,
                'description': 'Отсутствует Clean Architecture',
                'suggestion': 'Разделите код на слои: presentation, domain, data'
            })
        
        return bugs
    
    async def _classify_bugs_intelligently(self, bugs: List[Dict[str, Any]], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """ПРИНИМАЕТ РЕШЕНИЕ: как классифицировать баги"""
        classified_bugs = []
        
        for bug in bugs:
            # Агент решает серьезность бага на основе контекста
            severity = self._determine_bug_severity(bug, data)
            bug['severity'] = severity
            classified_bugs.append(bug)
        
        return classified_bugs
    
    def _determine_bug_severity(self, bug: Dict[str, Any], data: Dict[str, Any]) -> str:
        """ПРИНИМАЕТ РЕШЕНИЕ: определяет серьезность бага"""
        bug_type = bug.get('type', '')
        overall_score = data.get('overall_score', 0)
        
        # Агент адаптирует серьезность на основе состояния проекта
        if bug_type == 'critical_lifecycle':
            return 'critical'
        elif bug_type == 'memory_leak':
            return 'high' if overall_score < 0.6 else 'medium'
        elif bug_type == 'null_pointer_risk':
            return 'high' if overall_score < 0.5 else 'medium'
        elif bug_type == 'performance_issue':
            return 'medium' if overall_score < 0.7 else 'low'
        elif bug_type == 'security_issue':
            return 'critical' if 'password' in bug.get('description', '') else 'high'
        else:
            return 'medium'
    
    def _notify_previous_agent_about_bugs(self, bugs: List[Dict[str, Any]]):
        """ПРИНИМАЕТ РЕШЕНИЕ: уведомляет предыдущего агента о найденных багах"""
        critical_bugs = [b for b in bugs if b.get('severity') == 'critical']
        
        if critical_bugs:
            # Агент решает уведомить Code Analyzer о критических багах
            self.send_message('real_code_analyzer', 'bug_detection_feedback', {
                'total_bugs': len(bugs),
                'critical_bugs': critical_bugs,
                'message': f'Найдено {len(critical_bugs)} критических багов'
            })
            logger.info(f"Агент {self.name} уведомил Code Analyzer о {len(critical_bugs)} критических багах")
    
    def _find_line_number(self, content: str, pattern: str) -> int:
        """Находит номер строки с паттерном"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                return i + 1
        return 0
    
    def _group_bugs_by_severity(self, bugs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Группирует баги по серьезности"""
        grouped = {level: [] for level in self.severity_levels}
        
        for bug in bugs:
            severity = bug.get('severity', 'medium')
            if severity in grouped:
                grouped[severity].append(bug)
        
        return grouped
    
    def _group_bugs_by_category(self, bugs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Группирует баги по категориям"""
        grouped = {}
        
        for bug in bugs:
            category = bug.get('category', 'general')
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(bug)
        
        return grouped
    
    def _load_bug_patterns(self) -> Dict[str, Any]:
        """Загружает паттерны для поиска багов"""
        return {
            'memory_leaks': [
                r'static.*Context',
                r'static.*Activity',
                r'static.*Fragment'
            ],
            'null_pointer': [
                r'!!',
                r'\.get\(\)',
                r'\.value'
            ],
            'performance': [
                r'findViewById.*for',
                r'new.*for',
                r'RecyclerView.*Adapter'
            ],
            'security': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'SharedPreferences.*MODE_',
                r'Log\..*password'
            ]
        }
    
    async def process_message(self, message: AgentMessage):
        """Обрабатывает сообщения от других агентов"""
        if message.message_type == "request_bug_detection":
            result = await self.process(message.data)
            self.send_message(message.sender, "bug_detection_complete", result)
            
        elif message.message_type == "update_scan_mode":
            # Агент может изменить режим поиска по запросу
            new_mode = message.data.get('mode', 'standard')
            self.scan_mode = new_mode
            logger.info(f"Агент {self.name} изменил режим поиска на: {new_mode}")
            
        elif message.message_type == "analysis_feedback":
            # Получаем обратную связь от Code Analyzer
            feedback = message.data
            self._process_analysis_feedback(feedback)
    
    def _process_analysis_feedback(self, feedback: Dict[str, Any]):
        """Обрабатывает обратную связь от Code Analyzer"""
        overall_score = feedback.get('overall_score', 0)
        
        # Агент может изменить свои пороги на основе анализа
        if overall_score < 0.4:
            self.max_bugs_threshold = 20  # Снижаем порог для плохих проектов
            logger.info(f"Агент {self.name} снизил порог багов до 20 - проект в плохом состоянии")
        elif overall_score > 0.8:
            self.max_bugs_threshold = 100  # Повышаем порог для хороших проектов
            logger.info(f"Агент {self.name} повысил порог багов до 100 - проект в хорошем состоянии")
    
    # НЕЙРОННЫЕ МЕТОДЫ ПОИСКА БАГОВ
    async def _perform_neural_bug_scan(self, data: Dict[str, Any], focus_areas: List[str]) -> List[Dict[str, Any]]:
        """Выполняет поиск багов с помощью нейронки"""
        logger.info(f"Запускаю нейронный поиск багов в областях: {focus_areas}")
        
        project_path = data.get('project_path')
        project_structure = data.get('project_structure', {})
        
        # Собираем файлы для анализа
        files_to_analyze = []
        for category, files in project_structure.items():
            if isinstance(files, list) and files:
                for file_path in files[:5]:  # Берем по 5 файлов из каждой категории
                    # Исправляем путь - добавляем app/src/ перед main/java/
                    if file_path.startswith('main/java/'):
                        full_path = Path(project_path) / 'app' / 'src' / file_path
                    elif file_path.startswith('main/'):
                        full_path = Path(project_path) / 'app' / 'src' / file_path
                    else:
                        full_path = Path(project_path) / file_path
                    
                    logger.info(f"Пытаюсь прочитать файл для поиска багов: {full_path}")
                    if full_path.exists():
                        try:
                            content = full_path.read_text(encoding='utf-8')
                            files_to_analyze.append({
                                'path': str(file_path),
                                'content': content[:1500],  # Ограничиваем размер
                                'category': category
                            })
                            logger.info(f"✅ Успешно прочитан файл для поиска багов: {file_path}")
                        except Exception as e:
                            logger.warning(f"Не удалось прочитать {file_path}: {e}")
                    else:
                        logger.warning(f"Файл не найден для поиска багов: {full_path}")
        
        if not files_to_analyze:
            logger.warning("Нет файлов для поиска багов!")
            return []
        
        # Анализируем через GPT-4
        try:
            logger.info(f"Отправляю запрос к GPT-4 для поиска багов в {len(files_to_analyze)} файлах")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": f"""Ты эксперт по Android разработке и поиску багов. Проанализируй код и найди баги в областях: {', '.join(focus_areas)}.

Верни JSON в следующем формате:
{{
  "critical_bugs": [
    {{
      "file": "путь/к/файлу.kt",
      "description": "Описание бага",
      "line": 42,
      "type": "тип_бага"
    }}
  ],
  "architecture_issues": [
    {{
      "file": "путь/к/файлу.kt", 
      "description": "Описание проблемы архитектуры",
      "line": 15,
      "type": "архитектурная_проблема"
    }}
  ],
  "performance_issues": [
    {{
      "file": "путь/к/файлу.kt",
      "description": "Описание проблемы производительности", 
      "line": 30,
      "type": "проблема_производительности"
    }}
  ],
  "security_issues": [
    {{
      "file": "путь/к/файлу.kt",
      "description": "Описание проблемы безопасности",
      "line": 25,
      "type": "проблема_безопасности"
    }}
  ]
}}

Для каждого бага обязательно укажи:
- file: относительный путь к файлу
- description: подробное описание проблемы
- line: номер строки (если возможно)
- type: тип проблемы"""
                    },
                    {
                        "role": "user",
                        "content": f"Проанализируй эти Android файлы на баги:\n\n{json.dumps(files_to_analyze, ensure_ascii=False, indent=2)}"
                    }
                ],
                temperature=0.1
            )
            
            raw_content = response.choices[0].message.content
            logger.info(f"Получен ответ от GPT-4 для поиска багов (полный): {raw_content}")
            
            if not raw_content.strip():
                logger.error("GPT-4 вернул пустой ответ для поиска багов!")
                raise ValueError("GPT-4 вернул пустой ответ для поиска багов")
            
            # Извлекаем JSON из ответа GPT-4
            import re
            json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                logger.info(f"Извлечен JSON багов: {json_str}")
                bugs_data = json.loads(json_str)
                
                # Преобразуем в массив багов
                bugs = []
                if 'critical_bugs' in bugs_data:
                    for bug in bugs_data['critical_bugs']:
                        bug['severity'] = 'critical'
                        bug['file'] = bug.get('file', 'unknown')
                        bug['description'] = bug.get('description', bug.get('bug_description', 'No description'))
                        bugs.append(bug)
                if 'architecture_issues' in bugs_data:
                    for bug in bugs_data['architecture_issues']:
                        bug['severity'] = 'medium'
                        bug['file'] = bug.get('file', 'unknown')
                        bug['description'] = bug.get('description', bug.get('issue_description', 'No description'))
                        bugs.append(bug)
                if 'performance_issues' in bugs_data:
                    for bug in bugs_data['performance_issues']:
                        bug['severity'] = 'medium'
                        bug['file'] = bug.get('file', 'unknown')
                        bug['description'] = bug.get('description', bug.get('issue_description', 'No description'))
                        bugs.append(bug)
                if 'security_issues' in bugs_data:
                    for bug in bugs_data['security_issues']:
                        bug['severity'] = 'high'
                        bug['file'] = bug.get('file', 'unknown')
                        bug['description'] = bug.get('description', bug.get('issue_description', 'No description'))
                        bugs.append(bug)
            else:
                logger.error(f"Не найден JSON в ответе GPT-4: {raw_content}")
                raise ValueError("Не найден JSON в ответе GPT-4")
            
            logger.info(f"Успешно найдено {len(bugs)} багов")
            return bugs
            
        except Exception as e:
            logger.error(f"Ошибка нейронного поиска багов: {str(e)}")
            raise e
    
    def can_continue(self, data: Dict[str, Any]) -> bool:
        """ПРИНИМАЕТ РЕШЕНИЕ: может ли агент продолжить обработку"""
        # Bug Detector - последний агент в цепочке, не передает дальше
        return False
    
    def should_stop(self, data: Dict[str, Any]) -> bool:
        """ПРИНИМАЕТ РЕШЕНИЕ: должен ли агент остановить обработку"""
        # Bug Detector - последний агент, всегда завершает цепочку
        return True
