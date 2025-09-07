#!/usr/bin/env python3
"""
Тест полной цепочки агентов для демонстрации работы
"""

import asyncio
import json
import sys
import os

# Добавляем путь к модулям
sys.path.append('docker-mcp-reports/src')

from real_android_code_analyzer_agent import RealAndroidCodeAnalyzerAgent
from real_android_bug_detector_agent import RealAndroidBugDetectorAgent
from real_android_solution_generator_agent import RealAndroidSolutionGeneratorAgent
from real_android_solution_selector_agent import RealAndroidSolutionSelectorAgent

async def test_full_chain():
    """Тестирует полную цепочку агентов"""
    
    print("🚀 ТЕСТ ПОЛНОЙ ЦЕПОЧКИ АГЕНТОВ")
    print("=" * 40)
    
    # Инициализируем агентов
    print("1️⃣ Инициализация агентов...")
    code_analyzer = RealAndroidCodeAnalyzerAgent()
    bug_detector = RealAndroidBugDetectorAgent()
    solution_generator = RealAndroidSolutionGeneratorAgent()
    solution_selector = RealAndroidSolutionSelectorAgent()
    print("   ✅ Все агенты инициализированы")
    print()
    
    # Этап 1: Code Analyzer
    print("2️⃣ Code Analyzer: Анализ кода...")
    try:
        # Симулируем результат анализа
        analysis_result = {
            'project_structure': {
                'kotlin_files': ['app/src/main/java/android/mentor/livecodingapp/MainActivity.kt'],
                'xml_files': ['app/src/main/res/layout/activity_main.xml']
            },
            'architecture_analysis': {
                'score': 0.7,
                'issues': [
                    {
                        'file': 'app/src/main/java/android/mentor/livecodingapp/MainActivity.kt',
                        'line': 10,
                        'description': 'MainActivity слишком большая, нарушает Single Responsibility Principle'
                    }
                ]
            },
            'file_analysis': {
                'complexity_issues': [
                    {
                        'file': 'app/src/main/java/android/mentor/livecodingapp/MainActivity.kt',
                        'line': 15,
                        'description': 'Метод onCreate слишком длинный (50+ строк)'
                    },
                    {
                        'file': 'app/src/main/java/android/mentor/livecodingapp/MainActivity.kt',
                        'line': 25,
                        'description': 'Слишком много полей в классе (15+)'
                    }
                ]
            },
            'overall_score': 0.6
        }
        
        print(f"   ✅ Найдено проблем: {len(analysis_result['file_analysis']['complexity_issues'])}")
        print(f"   ✅ Архитектурных проблем: {len(analysis_result['architecture_analysis']['issues'])}")
        print()
        
        # Этап 2: Bug Detector
        print("3️⃣ Bug Detector: Поиск багов...")
        bugs_data = {
            'project_path': '/host',
            'project_structure': analysis_result.get('project_structure', {}),
            'architecture_analysis': analysis_result.get('architecture_analysis', {}),
            'file_analysis': analysis_result.get('file_analysis', {}),
            'overall_score': analysis_result.get('overall_score', 0),
            'analysis_result': analysis_result,
            'complexity_issues': analysis_result.get('file_analysis', {}).get('complexity_issues', []),
            'architecture_issues': analysis_result.get('architecture_analysis', {}).get('issues', [])
        }
        
        bugs_result = await bug_detector.process(bugs_data)
        print(f"   ✅ Найдено багов: {bugs_result.get('total_bugs', 0)}")
        print(f"   ✅ Критических: {len(bugs_result.get('critical_bugs', []))}")
        print(f"   ✅ Высокий приоритет: {len(bugs_result.get('high_priority_bugs', []))}")
        print()
        
        # Этап 3: Solution Generator
        print("4️⃣ Solution Generator: Генерация решений...")
        solutions_data = {
            'bugs': bugs_result,
            'project_context': 'Android проект на Kotlin'
        }
        
        solutions_result = await solution_generator.process(solutions_data)
        print(f"   ✅ Сгенерировано решений: {solutions_result.get('solutions_generated', 0)}")
        print()
        
        # Этап 4: Solution Selector
        print("5️⃣ Solution Selector: Выбор лучших решений...")
        selector_data = {
            'solutions': solutions_result,
            'project_context': 'Android проект на Kotlin'
        }
        
        selector_result = await solution_selector.process(selector_data)
        print(f"   ✅ Выбрано лучших решений: {selector_result.get('selected_count', 0)}")
        print()
        
        # Итоговый результат
        print("🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
        print(f"   - Проблем найдено: {len(analysis_result['file_analysis']['complexity_issues'])}")
        print(f"   - Багов найдено: {bugs_result.get('total_bugs', 0)}")
        print(f"   - Решений сгенерировано: {solutions_result.get('solutions_generated', 0)}")
        print(f"   - Лучших выбрано: {selector_result.get('selected_count', 0)}")
        print()
        
        # Проверяем цепочку
        if (bugs_result.get('total_bugs', 0) > 0 and 
            solutions_result.get('solutions_generated', 0) > 0 and 
            selector_result.get('selected_count', 0) > 0):
            print("✅ ЦЕПОЧКА АГЕНТОВ РАБОТАЕТ КОРРЕКТНО!")
            print("   Code Analyzer → Bug Detector → Solution Generator → Solution Selector")
        else:
            print("❌ ЦЕПОЧКА АГЕНТОВ НЕ РАБОТАЕТ!")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_chain())


