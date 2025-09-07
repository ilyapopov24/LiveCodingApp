#!/usr/bin/env python3
"""
Real Android Code Analyzer Agent - настоящий агент с принятием решений
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

class RealAndroidCodeAnalyzerAgent(BaseAgent):
    """Настоящий агент для анализа Android кода с принятием решений"""
    
    def __init__(self):
        super().__init__("real_code_analyzer")
        self.supported_extensions = ['.kt', '.java', '.xml']
        self.complexity_threshold = 10
        self.file_size_threshold = 500
        self.analysis_threshold = 0.7
        self.analysis_mode = 'standard'  # standard, quick, deep
        self.decision_history = []
        
        # Инициализируем OpenAI клиент
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY не установлен")
        self.openai_client = openai.OpenAI(api_key=api_key)
        
        logger.info(f"Настоящий агент {self.name} инициализирован")
    
    async def process(self, data: Any) -> Dict[str, Any]:
        """Анализирует Android проект с принятием решений"""
        project_path = data if isinstance(data, str) else data.get('project_path')
        
        # Преобразуем путь для работы внутри Docker контейнера
        if project_path:
            if project_path.startswith('/Users/ilyapopov/Downloads/LiveCodingApp'):
                # Заменяем хост-путь на Docker-путь
                project_path = '/host'
            elif project_path.startswith('/host/LiveCodingApp'):
                # Убираем лишний /LiveCodingApp из Docker-пути
                project_path = '/host'
            elif not project_path.startswith('/host'):
                # Если путь не начинается с /host, заменяем на /host
                project_path = '/host'
        
        if not project_path or not os.path.exists(project_path):
            raise ValueError(f"Проект не найден: {project_path}")
        
        logger.info(f"Агент {self.name} начинает анализ: {project_path}")
        
        try:
            # ПРИНИМАЕМ РЕШЕНИЕ: какой режим анализа использовать?
            analysis_mode = self._decide_analysis_mode(project_path)
            self.analysis_mode = analysis_mode
            logger.info(f"Агент {self.name} выбрал режим анализа: {analysis_mode}")
            
            # Выполняем анализ в выбранном режиме
            result = await self._perform_analysis(project_path, analysis_mode)
            
            # ПРИНИМАЕМ РЕШЕНИЕ: нужен ли поиск багов?
            needs_bug_detection = self._decide_bug_detection_necessity(result)
            result['needs_bug_detection'] = needs_bug_detection
            result['bug_detection_priority'] = self._determine_bug_priority(result)
            
            # ПРИНИМАЕМ РЕШЕНИЕ: какие данные передать следующему агенту?
            result['next_agent_data'] = self._prepare_data_for_next_agent(result)
            
            # Записываем решение в историю
            self.decision_history.append({
                'timestamp': asyncio.get_event_loop().time(),
                'decision': 'analysis_mode',
                'value': analysis_mode,
                'reasoning': f"Выбран режим {analysis_mode} на основе размера проекта"
            })
            
            logger.info(f"Агент {self.name} завершил анализ. Нужен поиск багов: {needs_bug_detection}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка в агенте {self.name}: {str(e)}")
            raise
    
    def _decide_analysis_mode(self, project_path: str) -> str:
        """ПРИНИМАЕТ РЕШЕНИЕ: какой режим анализа использовать"""
        try:
            # Анализируем размер Android проекта
            project_dir = Path(project_path)
            total_files = 0
            
            # Ищем файлы в Android модулях
            android_modules = ['app', 'domain', 'presentation', 'data', 'lib']
            for module in android_modules:
                module_path = project_dir / module
                if module_path.exists():
                    kotlin_files = list(module_path.glob('**/*.kt'))
                    java_files = list(module_path.glob('**/*.java'))
                    total_files += len(kotlin_files) + len(java_files)
            
            # ПРИНИМАЕМ РЕШЕНИЕ на основе размера
            if total_files > 100:
                return 'quick'  # Быстрый анализ для больших проектов
            elif total_files > 20:
                return 'standard'  # Стандартный анализ
            else:
                return 'deep'  # Глубокий анализ для маленьких проектов
                
        except Exception as e:
            logger.error(f"Ошибка при определении режима анализа: {str(e)}")
            raise e
    
    def _decide_bug_detection_necessity(self, analysis_result: Dict[str, Any]) -> bool:
        """ПРИНИМАЕТ РЕШЕНИЕ: нужен ли поиск багов"""
        overall_score = analysis_result.get('overall_score', 0)
        complexity_issues = len(analysis_result.get('file_analysis', {}).get('complexity_issues', []))
        architecture_score = analysis_result.get('architecture_analysis', {}).get('architecture_score', 0)
        
        # ПРИНИМАЕМ РЕШЕНИЕ на основе анализа
        if overall_score < 0.5:
            return True  # Плохой проект - точно нужен поиск багов
        elif complexity_issues > 5:
            return True  # Много проблем со сложностью
        elif architecture_score < 0.6:
            return True  # Плохая архитектура
        elif overall_score > 0.8 and complexity_issues == 0:
            return False  # Отличный проект - можно пропустить поиск багов
        else:
            return True  # По умолчанию ищем баги
    
    def _determine_bug_priority(self, analysis_result: Dict[str, Any]) -> str:
        """ПРИНИМАЕТ РЕШЕНИЕ: приоритет поиска багов"""
        overall_score = analysis_result.get('overall_score', 0)
        critical_issues = analysis_result.get('file_analysis', {}).get('complexity_issues', [])
        
        if overall_score < 0.3 or len(critical_issues) > 10:
            return 'critical'
        elif overall_score < 0.6 or len(critical_issues) > 5:
            return 'high'
        else:
            return 'normal'
    
    def _prepare_data_for_next_agent(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """ПРИНИМАЕТ РЕШЕНИЕ: какие данные передать следующему агенту"""
        # Агент решает, что передать Bug Detector
        priority = analysis_result.get('bug_detection_priority', 'normal')
        
        if priority == 'critical':
            # Критический приоритет - передаем все данные
            return {
                'project_path': analysis_result.get('project_path'),
                'project_structure': analysis_result.get('project_structure', {}),
                'file_analysis': analysis_result.get('file_analysis', {}),
                'architecture_analysis': analysis_result.get('architecture_analysis', {}),
                'scan_mode': 'aggressive',
                'focus_areas': ['memory_leaks', 'performance', 'security', 'architecture']
            }
        elif priority == 'high':
            # Высокий приоритет - фокус на проблемных областях
            return {
                'project_path': analysis_result.get('project_path'),
                'project_structure': analysis_result.get('project_structure', {}),
                'file_analysis': analysis_result.get('file_analysis', {}),
                'scan_mode': 'focused',
                'focus_areas': ['memory_leaks', 'performance']
            }
        else:
            # Обычный приоритет - стандартный поиск
            return {
                'project_path': analysis_result.get('project_path'),
                'project_structure': analysis_result.get('project_structure', {}),
                'scan_mode': 'standard',
                'focus_areas': ['critical_bugs']
            }
    
    async def _perform_analysis(self, project_path: str, mode: str) -> Dict[str, Any]:
        """Выполняет анализ в выбранном режиме"""
        if mode == 'quick':
            return await self._quick_analysis(project_path)
        elif mode == 'deep':
            return await self._deep_analysis(project_path)
        else:
            return await self._standard_analysis(project_path)
    
    async def _quick_analysis(self, project_path: str) -> Dict[str, Any]:
        """Быстрый анализ для больших проектов с нейронным анализом"""
        logger.info(f"Выполняю быстрый анализ проекта: {project_path}")
        
        # Сканируем структуру
        project_structure = await self._scan_project_structure(project_path)
        file_count = sum(len(files) for files in project_structure.values() if isinstance(files, list))
        logger.info(f"Сканирована структура проекта: {len(project_structure)} категорий, {file_count} файлов")
        logger.info(f"Структура проекта: {project_structure}")
        
        # НЕЙРОННЫЙ АНАЛИЗ: анализируем ключевые файлы
        file_analysis = await self._analyze_files_with_neural(project_path, project_structure, max_files=10)
        architecture_analysis = await self._analyze_architecture_with_neural(project_structure)
        
        overall_score = self._calculate_overall_score(file_analysis, architecture_analysis, {}, {})
        
        # Собираем содержимое файлов для передачи следующему агенту
        file_contents = {}
        files_to_analyze = await self._collect_android_files_for_analysis(project_path)
        for file_info in files_to_analyze:
            file_contents[file_info['path']] = file_info['content']
        
        return {
            'project_path': project_path,
            'project_structure': project_structure,
            'file_contents': file_contents,  # Добавляем содержимое файлов
            'file_analysis': file_analysis,
            'architecture_analysis': architecture_analysis,
            'overall_score': overall_score,
            'analysis_mode': 'quick'
        }
    
    async def _standard_analysis(self, project_path: str) -> Dict[str, Any]:
        """Стандартный анализ"""
        logger.info(f"Выполняю стандартный анализ проекта: {project_path}")
        
        # Стандартный анализ - полная проверка
        project_structure = await self._scan_project_structure(project_path)
        file_analysis = await self._analyze_files(project_path, project_structure)
        architecture_analysis = await self._analyze_architecture(project_structure)
        
        overall_score = self._calculate_overall_score(file_analysis, architecture_analysis, {}, {})
        
        return {
            'project_path': project_path,
            'project_structure': project_structure,
            'file_analysis': file_analysis,
            'architecture_analysis': architecture_analysis,
            'overall_score': overall_score,
            'analysis_mode': 'standard'
        }
    
    async def _deep_analysis(self, project_path: str) -> Dict[str, Any]:
        """Глубокий анализ для маленьких проектов"""
        logger.info(f"Выполняю глубокий анализ проекта: {project_path}")
        
        # Глубокий анализ - максимальная детализация
        project_structure = await self._scan_project_structure(project_path)
        file_analysis = await self._analyze_files(project_path, project_structure)
        architecture_analysis = await self._analyze_architecture(project_structure)
        dependency_analysis = await self._analyze_dependencies(project_path)
        code_quality = await self._analyze_code_quality(project_path, project_structure)
        
        overall_score = self._calculate_overall_score(file_analysis, architecture_analysis, dependency_analysis, code_quality)
        
        return {
            'project_path': project_path,
            'project_structure': project_structure,
            'file_analysis': file_analysis,
            'architecture_analysis': architecture_analysis,
            'dependency_analysis': dependency_analysis,
            'code_quality': code_quality,
            'overall_score': overall_score,
            'analysis_mode': 'deep'
        }
    
    async def process_message(self, message: AgentMessage):
        """Обрабатывает сообщения от других агентов"""
        if message.message_type == "request_analysis":
            result = await self.process(message.data)
            self.send_message(message.sender, "analysis_complete", result)
            
        elif message.message_type == "update_analysis_mode":
            # Агент может изменить режим анализа по запросу
            new_mode = message.data.get('mode', 'standard')
            self.analysis_mode = new_mode
            logger.info(f"Агент {self.name} изменил режим анализа на: {new_mode}")
            
        elif message.message_type == "request_project_health":
            # Отвечаем на запрос о состоянии проекта
            health_status = self._assess_project_health(message.data)
            self.send_message(message.sender, "project_health_response", health_status)
            
        elif message.message_type == "bug_detection_feedback":
            # Получаем обратную связь от Bug Detector
            feedback = message.data
            self._process_bug_detection_feedback(feedback)
    
    def _process_bug_detection_feedback(self, feedback: Dict[str, Any]):
        """Обрабатывает обратную связь от Bug Detector"""
        bug_count = feedback.get('total_bugs', 0)
        critical_bugs = feedback.get('critical_bugs', [])
        
        # Агент может изменить свои пороги на основе найденных багов
        if len(critical_bugs) > 5:
            self.analysis_threshold = 0.8  # Повышаем требования
            logger.info(f"Агент {self.name} повысил порог анализа до 0.8 из-за критических багов")
        elif bug_count == 0:
            self.analysis_threshold = 0.6  # Снижаем требования
            logger.info(f"Агент {self.name} снизил порог анализа до 0.6 - багов не найдено")
    
    def can_continue(self, data: Dict[str, Any]) -> bool:
        """ПРИНИМАЕТ РЕШЕНИЕ: может ли агент продолжить обработку"""
        needs_bug_detection = data.get('needs_bug_detection', True)
        
        # Агент решает, нужно ли передавать данные дальше
        # Если нужен поиск багов - передаем дальше независимо от оценки
        logger.info(f"Проверяю can_continue: needs_bug_detection={needs_bug_detection}")
        return needs_bug_detection
    
    def should_stop(self, data: Dict[str, Any]) -> bool:
        """ПРИНИМАЕТ РЕШЕНИЕ: должен ли агент остановить обработку"""
        overall_score = data.get('overall_score', 0)
        
        # Останавливаем цепочку только в критических случаях
        return overall_score < 0.2
    
    def _assess_project_health(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Оценивает состояние проекта"""
        overall_score = data.get('overall_score', 0)
        
        if overall_score >= 0.8:
            return {"status": "excellent", "score": overall_score, "message": "Проект в отличном состоянии"}
        elif overall_score >= 0.6:
            return {"status": "good", "score": overall_score, "message": "Проект в хорошем состоянии"}
        elif overall_score >= 0.4:
            return {"status": "fair", "score": overall_score, "message": "Проект требует улучшений"}
        else:
            return {"status": "poor", "score": overall_score, "message": "Проект в критическом состоянии"}
    
    # Методы анализа (упрощенные версии из предыдущего кода)
    async def _scan_project_structure(self, project_path: str) -> Dict[str, Any]:
        """Сканирует структуру Android проекта"""
        structure = {
            'activities': [],
            'fragments': [],
            'viewmodels': [],
            'repositories': [],
            'adapters': [],
            'models': [],
            'layouts': [],
            'resources': [],
            'tests': []
        }
        
        project_dir = Path(project_path)
        
        # Android структура: ищем в app/, domain/, presentation/, data/ модулях
        android_modules = ['app', 'domain', 'presentation', 'data', 'lib']
        
        for module in android_modules:
            module_path = project_dir / module
            if module_path.exists():
                # Ищем в src/main/java/ или src/main/kotlin/
                java_src = module_path / 'src' / 'main' / 'java'
                kotlin_src = module_path / 'src' / 'main' / 'kotlin'
                
                if java_src.exists():
                    await self._scan_directory(java_src, structure)
                if kotlin_src.exists():
                    await self._scan_directory(kotlin_src, structure)
                
                # Ищем XML файлы в res/
                res_path = module_path / 'src' / 'main' / 'res'
                if res_path.exists():
                    await self._scan_directory(res_path, structure)
        
        # Также ищем в корне проекта (для старых проектов)
        root_src = project_dir / 'src' / 'main'
        if root_src.exists():
            await self._scan_directory(root_src, structure)
        
        return structure
    
    async def _scan_directory(self, directory: Path, structure: Dict):
        """Рекурсивно сканирует директорию"""
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.kt', '.java', '.xml']:
                # Вычисляем относительный путь от корня проекта
                # Ищем корень проекта (где находится app/, domain/, presentation/, data/)
                project_root = directory
                while project_root.name != 'src' and project_root.parent != project_root:
                    project_root = project_root.parent
                project_root = project_root.parent  # Поднимаемся выше src
                
                try:
                    relative_path = str(file_path.relative_to(project_root))
                    # Исправляем путь: если файл в app/src/main/java/, то путь должен быть app/src/main/java/...
                    if not relative_path.startswith('app/') and 'app/src/main' in str(file_path):
                        # Если файл в app/src/main/, но relative_path не начинается с app/, исправляем
                        parts = relative_path.split('/')
                        if 'src' in parts and 'main' in parts:
                            src_index = parts.index('src')
                            relative_path = '/'.join(parts[src_index:])
                except ValueError:
                    # Если не можем вычислить относительный путь, используем имя файла
                    relative_path = file_path.name
                
                if file_path.suffix in ['.kt', '.java']:
                    await self._categorize_kotlin_java_file(file_path, structure, relative_path)
                elif file_path.suffix == '.xml':
                    if 'layout' in str(file_path):
                        structure['layouts'].append(relative_path)
                    else:
                        structure['resources'].append(relative_path)
    
    async def _categorize_kotlin_java_file(self, file_path: Path, structure: Dict, relative_path: str):
        """Категоризирует Kotlin/Java файлы"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            if re.search(r'class\s+\w+.*Activity', content) or 'AppCompatActivity' in content:
                structure['activities'].append(relative_path)
            elif re.search(r'class\s+\w+.*Fragment', content) or 'Fragment()' in content:
                structure['fragments'].append(relative_path)
            elif 'ViewModel' in content and 'class' in content:
                structure['viewmodels'].append(relative_path)
            elif 'Repository' in content and 'class' in content:
                structure['repositories'].append(relative_path)
            elif 'Adapter' in content and 'class' in content:
                structure['adapters'].append(relative_path)
            elif 'data class' in content:
                structure['models'].append(relative_path)
                
        except Exception as e:
            logger.warning(f"Не удалось прочитать файл {file_path}: {str(e)}")
    
    async def _analyze_files(self, project_path: str, project_structure: Dict) -> Dict[str, Any]:
        """Анализирует файлы проекта"""
        analysis = {
            'total_files': 0,
            'kotlin_files': 0,
            'java_files': 0,
            'xml_files': 0,
            'complexity_issues': [],
            'size_issues': []
        }
        
        all_files = []
        for category in project_structure.values():
            if isinstance(category, list):
                all_files.extend(category)
        
        analysis['total_files'] = len(all_files)
        
        for file_path in all_files:
            if file_path.endswith('.kt'):
                analysis['kotlin_files'] += 1
            elif file_path.endswith('.java'):
                analysis['java_files'] += 1
            elif file_path.endswith('.xml'):
                analysis['xml_files'] += 1
        
        return analysis
    
    async def _collect_android_files_for_analysis(self, project_path: str) -> List[Dict[str, Any]]:
        """Собирает .kt файлы из presentation/ui/ для анализа с лимитом 15000 токенов"""
        logger.info("Собираю .kt файлы из presentation/ui/ для анализа")
        
        project_dir = Path(project_path)
        files_to_analyze = []
        total_tokens = 0
        max_tokens = 15000  # Лимит токенов
        
        # Ищем .kt файлы только в presentation/src/main/java/android/mentor/presentation/ui/
        ui_dir = project_dir / 'presentation' / 'src' / 'main' / 'java' / 'android' / 'mentor' / 'presentation' / 'ui'
        
        if not ui_dir.exists():
            logger.warning(f"Директория не найдена: {ui_dir}")
            return files_to_analyze
        
        # Собираем все .kt файлы из ui директории
        kotlin_files = []
        for kt_file in ui_dir.rglob('*.kt'):
            # Исключаем файлы из /build директорий
            if '/build/' not in str(kt_file):
                kotlin_files.append(kt_file)
        
        # Сортируем по размеру (сначала маленькие файлы)
        kotlin_files.sort(key=lambda f: f.stat().st_size if f.exists() else 0)
        
        # Добавляем .kt файлы пока не достигнем лимита токенов
        for kt_file in kotlin_files:
            if total_tokens >= max_tokens:
                break
                
            try:
                content = kt_file.read_text(encoding='utf-8')
                # Примерная оценка токенов (1 токен ≈ 4 символа)
                file_tokens = len(content) // 4
                
                if total_tokens + file_tokens <= max_tokens:
                    relative_path = str(kt_file.relative_to(project_dir))
                    files_to_analyze.append({
                        'path': relative_path,
                        'content': content,
                        'type': 'kotlin',
                        'tokens': file_tokens
                    })
                    total_tokens += file_tokens
                    logger.info(f"✅ Добавлен .kt файл: {relative_path} ({file_tokens} токенов)")
                else:
                    logger.info(f"⚠️ Пропущен .kt файл (превышение лимита): {kt_file.name}")
                    break
            except Exception as e:
                logger.warning(f"Не удалось прочитать .kt файл {kt_file}: {e}")
        
        logger.info(f"📊 Итого собрано .kt файлов из presentation/ui/: {len(files_to_analyze)}, токенов: {total_tokens}")
        return files_to_analyze
    
    async def _analyze_architecture(self, project_structure: Dict) -> Dict[str, Any]:
        """Анализирует архитектуру проекта"""
        architecture = {
            'has_mvvm': False,
            'has_clean_architecture': False,
            'has_repository_pattern': False,
            'architecture_score': 0.0
        }
        
        # Проверяем наличие MVVM
        if project_structure['viewmodels'] and project_structure['activities']:
            architecture['has_mvvm'] = True
        
        # Проверяем Clean Architecture
        if (project_structure['repositories'] and 
            project_structure['viewmodels'] and 
            project_structure['models']):
            architecture['has_clean_architecture'] = True
        
        # Проверяем Repository Pattern
        if project_structure['repositories']:
            architecture['has_repository_pattern'] = True
        
        # Вычисляем оценку архитектуры
        score = 0.0
        if architecture['has_mvvm']:
            score += 0.3
        if architecture['has_clean_architecture']:
            score += 0.4
        if architecture['has_repository_pattern']:
            score += 0.2
        
        architecture['architecture_score'] = score
        return architecture
    
    async def _analyze_dependencies(self, project_path: str) -> Dict[str, Any]:
        """Анализирует зависимости проекта"""
        return {
            'dependencies': [],
            'gradle_files': []
        }
    
    async def _analyze_code_quality(self, project_path: str, project_structure: Dict) -> Dict[str, Any]:
        """Анализирует качество кода"""
        return {
            'code_smells': [],
            'maintainability_score': 0.8,
            'readability_score': 0.8
        }
    
    # НЕЙРОННЫЕ МЕТОДЫ АНАЛИЗА
    async def _analyze_files_with_neural(self, project_path: str, project_structure: Dict, max_files: int = 20) -> Dict[str, Any]:
        """Анализирует файлы с помощью нейронки"""
        logger.info("Запускаю нейронный анализ файлов")
        
        # Собираем файлы для анализа по новой логике
        files_to_analyze = await self._collect_android_files_for_analysis(project_path)
        
        if not files_to_analyze:
            logger.warning("Нет файлов для анализа!")
            return {'total_files': 0, 'complexity_issues': []}
        
        # Анализируем через GPT-4
        try:
            logger.info(f"Отправляю запрос к GPT-4 для анализа {len(files_to_analyze)} файлов")
            
            # Формируем детальное описание файлов для GPT (полное содержимое)
            files_description = []
            total_tokens = 0
            for file_info in files_to_analyze:
                files_description.append({
                    'path': file_info['path'],
                    'type': file_info['type'],
                    'tokens': file_info['tokens'],
                    'content': file_info['content']  # Полное содержимое без обрезания
                })
                total_tokens += file_info['tokens']
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """Ты эксперт по Android разработке. Проанализируй код и найди проблемы со сложностью, архитектурой и качеством.

Верни JSON в формате:
{
    "complexity_issues": [
        {
            "file": "путь/к/файлу.kt",
            "description": "описание проблемы",
            "severity": "low/medium/high",
            "line": 42
        }
    ],
    "architecture_issues": [
        {
            "file": "путь/к/файлу.kt", 
            "description": "описание архитектурной проблемы",
            "severity": "medium/high",
            "line": 15
        }
    ],
    "code_smells": [
        {
            "file": "путь/к/файлу.kt",
            "description": "описание code smell",
            "severity": "low/medium",
            "line": 8
        }
    ],
    "overall_score": 0.85
}"""
                    },
                    {
                        "role": "user",
                        "content": f"Проанализируй эти Android файлы (всего {len(files_to_analyze)} файлов, {total_tokens} токенов). Файлы содержат полный код без обрезания:\n\n{json.dumps(files_description, ensure_ascii=False, indent=2)}"
                    }
                ],
                temperature=0.1
            )
            
            raw_content = response.choices[0].message.content
            logger.info(f"Получен ответ от GPT-4 (полный): {raw_content}")
            logger.info(f"Длина ответа: {len(raw_content)} символов")
            
            if not raw_content.strip():
                logger.error("GPT-4 вернул пустой ответ!")
                raise ValueError("GPT-4 вернул пустой ответ")
            
            # Извлекаем JSON из ответа GPT-4
            import re
            json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                logger.info(f"Извлечен JSON: {json_str}")
                analysis_result = json.loads(json_str)
            else:
                logger.error(f"Не найден JSON в ответе GPT-4: {raw_content}")
                raise ValueError("Не найден JSON в ответе GPT-4")
            
            logger.info(f"Успешно распарсен JSON: {analysis_result}")
            return analysis_result
        except Exception as e:
            logger.error(f"Ошибка нейронного анализа: {str(e)}")
            raise e
    
    async def _analyze_architecture_with_neural(self, project_structure: Dict) -> Dict[str, Any]:
        """Анализирует архитектуру с помощью нейронки"""
        logger.info("Запускаю нейронный анализ архитектуры")
        
        # Подготавливаем данные о структуре
        structure_summary = {
            'activities': len(project_structure.get('activities', [])),
            'fragments': len(project_structure.get('fragments', [])),
            'viewmodels': len(project_structure.get('viewmodels', [])),
            'repositories': len(project_structure.get('repositories', [])),
            'models': len(project_structure.get('models', [])),
            'layouts': len(project_structure.get('layouts', []))
        }
        
        try:
            logger.info(f"Отправляю запрос к GPT-4 для анализа архитектуры: {structure_summary}")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты эксперт по Android архитектуре. Проанализируй структуру проекта и оцени архитектуру по шкале 0-1. Верни JSON с оценкой."
                    },
                    {
                        "role": "user",
                        "content": f"Проанализируй архитектуру Android проекта: {json.dumps(structure_summary, ensure_ascii=False)}"
                    }
                ],
                temperature=0.1
            )
            
            raw_content = response.choices[0].message.content
            logger.info(f"Получен ответ от GPT-4 для архитектуры (полный): {raw_content}")
            logger.info(f"Длина ответа архитектуры: {len(raw_content)} символов")
            
            if not raw_content.strip():
                logger.error("GPT-4 вернул пустой ответ для архитектуры!")
                raise ValueError("GPT-4 вернул пустой ответ для архитектуры")
            
            # Извлекаем JSON из ответа GPT-4
            import re
            json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                logger.info(f"Извлечен JSON: {json_str}")
                architecture_result = json.loads(json_str)
            else:
                logger.error(f"Не найден JSON в ответе GPT-4: {raw_content}")
                raise ValueError("Не найден JSON в ответе GPT-4")
            
            logger.info(f"Успешно распарсен JSON архитектуры: {architecture_result}")
            return architecture_result
        except Exception as e:
            logger.error(f"Ошибка нейронного анализа архитектуры: {str(e)}")
            raise e
    
    def _calculate_overall_score(self, file_analysis: Dict, architecture_analysis: Dict, dependency_analysis: Dict, code_quality: Dict) -> float:
        """Вычисляет общую оценку проекта"""
        score = 0.0
        
        # Оценка архитектуры (40%)
        score += architecture_analysis.get('architecture_score', 0) * 0.4
        
        # Оценка качества кода (30%)
        maintainability = code_quality.get('maintainability_score', 0.8)
        readability = code_quality.get('readability_score', 0.8)
        quality_score = (maintainability + readability) / 2
        score += quality_score * 0.3
        
        # Оценка файлов (20%)
        total_files = file_analysis.get('total_files', 0)
        if total_files > 0:
            file_score = min(total_files / 50, 1.0)
            score += file_score * 0.2
        
        # Оценка зависимостей (10%)
        deps = dependency_analysis.get('dependencies', [])
        if deps:
            dep_score = min(len(deps) / 20, 1.0)
            score += dep_score * 0.1
        
        return min(score, 1.0)
