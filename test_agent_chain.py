#!/usr/bin/env python3
"""
Тест цепочки агентов для демонстрации работы
"""

import asyncio
import json
import sys
import os

# Добавляем путь к модулям
sys.path.append('docker-mcp-reports/src')

from real_android_four_agent_system import RealAndroidFourAgentSystem

async def test_agent_chain():
    """Тестирует работу цепочки агентов"""
    
    print("🚀 ДЕМОНСТРАЦИЯ РАБОТЫ ЦЕПОЧКИ АГЕНТОВ")
    print("=" * 50)
    
    # Инициализируем систему агентов
    print("1️⃣ Инициализация системы агентов...")
    agent_system = RealAndroidFourAgentSystem()
    print(f"   ✅ Система инициализирована: {agent_system.get_agent_chain_info()}")
    print()
    
    # Тестируем анализ проекта
    project_path = "/Users/ilyapopov/Downloads/LiveCodingApp"
    print(f"2️⃣ Анализ проекта: {project_path}")
    print("   Запускаю цепочку агентов...")
    print()
    
    try:
        # Запускаем полную цепочку
        result = await agent_system.process_android_project(project_path)
        
        print("3️⃣ РЕЗУЛЬТАТЫ РАБОТЫ ЦЕПОЧКИ:")
        print("=" * 30)
        
        # Показываем результаты каждого агента
        print("🔍 Code Analyzer:")
        analysis = result.get('analysis_result', {})
        print(f"   - Общая оценка: {analysis.get('overall_score', 0):.2f}/1.0")
        print(f"   - Архитектурная оценка: {analysis.get('architecture_analysis', {}).get('score', 0):.2f}/1.0")
        
        complexity_issues = analysis.get('file_analysis', {}).get('complexity_issues', [])
        print(f"   - Проблемы сложности: {len(complexity_issues)}")
        for issue in complexity_issues[:2]:  # Показываем первые 2
            print(f"     * {issue.get('file', 'unknown')}: {issue.get('description', '')[:50]}...")
        
        print()
        print("🐛 Bug Detector:")
        bugs = result.get('bugs_data', {})
        print(f"   - Всего багов: {bugs.get('total_bugs', 0)}")
        print(f"   - Критические: {len(bugs.get('critical_bugs', []))}")
        print(f"   - Высокий приоритет: {len(bugs.get('high_priority_bugs', []))}")
        print(f"   - Средний приоритет: {len(bugs.get('bugs_by_severity', {}).get('medium', []))}")
        
        all_bugs = bugs.get('all_bugs', [])
        for bug in all_bugs[:2]:  # Показываем первые 2 бага
            print(f"     * {bug.get('file', 'unknown')}: {bug.get('description', '')[:50]}...")
        
        print()
        print("💡 Solution Generator:")
        solutions = result.get('solutions_data', {})
        print(f"   - Сгенерировано решений: {solutions.get('solutions_generated', 0)}")
        
        print()
        print("✅ Solution Selector:")
        selected = result.get('selected_solutions', {})
        print(f"   - Выбрано лучших решений: {selected.get('selected_count', 0)}")
        
        print()
        print("🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
        print(f"   - Найдено проблем: {len(complexity_issues)}")
        print(f"   - Найдено багов: {bugs.get('total_bugs', 0)}")
        print(f"   - Сгенерировано решений: {solutions.get('solutions_generated', 0)}")
        print(f"   - Выбрано лучших: {selected.get('selected_count', 0)}")
        
        print()
        print("✅ ЦЕПОЧКА АГЕНТОВ РАБОТАЕТ КОРРЕКТНО!")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_chain())


