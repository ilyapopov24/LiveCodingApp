#!/usr/bin/env python3
"""
Тест Bug Detector для проверки правильности работы
"""

import asyncio
import json
import sys
import os

# Добавляем путь к модулям
sys.path.append('docker-mcp-reports/src')

from real_android_bug_detector_agent import RealAndroidBugDetectorAgent

async def test_bug_detector():
    """Тестирует Bug Detector с реальными данными"""
    
    print("🐛 ТЕСТ BUG DETECTOR")
    print("=" * 30)
    
    # Создаем агента
    agent = RealAndroidBugDetectorAgent()
    
    # Тестовые данные от Code Analyzer
    test_data = {
        'project_path': '/host',
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
        'overall_score': 0.6,
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
        ],
        'architecture_issues': [
            {
                'file': 'app/src/main/java/android/mentor/livecodingapp/MainActivity.kt',
                'line': 10,
                'description': 'MainActivity слишком большая, нарушает Single Responsibility Principle'
            }
        ]
    }
    
    print("📊 Тестовые данные:")
    print(f"  - complexity_issues: {len(test_data['complexity_issues'])}")
    print(f"  - architecture_issues: {len(test_data['architecture_issues'])}")
    print()
    
    print("🔍 Запуск Bug Detector...")
    try:
        result = await agent.process(test_data)
        
        print("✅ Результат Bug Detector:")
        print(f"  - Всего багов: {result.get('total_bugs', 0)}")
        print(f"  - Критические: {len(result.get('critical_bugs', []))}")
        print(f"  - Высокий приоритет: {len(result.get('high_priority_bugs', []))}")
        print(f"  - Средний приоритет: {len(result.get('bugs_by_severity', {}).get('medium', []))}")
        
        all_bugs = result.get('all_bugs', [])
        print(f"  - Все баги: {len(all_bugs)}")
        
        for i, bug in enumerate(all_bugs, 1):
            print(f"    {i}. {bug.get('file', 'unknown')}: {bug.get('description', '')}")
        
        print()
        if len(all_bugs) > 0:
            print("✅ Bug Detector работает правильно - нашел баги на основе проблем от Code Analyzer!")
        else:
            print("❌ Bug Detector НЕ работает - не нашел баги!")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_bug_detector())


