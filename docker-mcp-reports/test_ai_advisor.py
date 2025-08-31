#!/usr/bin/env python3
"""
Тестовый скрипт для AI Advisor MCP сервера
"""

import os
import sys
import logging

# Добавляем src в path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_advisor_mcp_server import GitHubAIAdvisorMCPServer

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ai_advisor():
    """Тестирует AI Advisor MCP сервер"""
    
    # Проверяем переменные окружения
    required_env_vars = ['GITHUB_TOKEN', 'OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Отсутствуют переменные окружения: {missing_vars}")
        logger.info("Убедитесь, что .env файл настроен правильно")
        return False
    
    try:
        # Создаем сервер
        logger.info("Создаю AI Advisor MCP сервер...")
        server = GitHubAIAdvisorMCPServer()
        
        # Проверяем доступные тулсы
        logger.info("Проверяю доступные тулсы...")
        tools = server.list_tools()
        logger.info(f"Найдено {len(tools)} тулсов:")
        
        for tool in tools:
            logger.info(f"  - {tool['name']}: {tool['description']}")
        
        # Тестируем анализ профиля
        logger.info("\nТестирую analyze_profile...")
        test_username = "ilyapopov24"
        
        result = server.call_tool("analyze_profile", {"username": test_username})
        
        if result and result.get('content'):
            logger.info("✅ analyze_profile выполнен успешно!")
            logger.info(f"Результат: {result['content'][0]['text'][:200]}...")
        else:
            logger.error("❌ analyze_profile вернул пустой результат")
            return False
        
        # Тестируем suggest_improvements
        logger.info("\nТестирую suggest_improvements...")
        result = server.call_tool("suggest_improvements", {
            "username": test_username,
            "focus_area": "repos"
        })
        
        if result and result.get('content'):
            logger.info("✅ suggest_improvements выполнен успешно!")
            logger.info(f"Результат: {result['content'][0]['text'][:200]}...")
        else:
            logger.error("❌ suggest_improvements вернул пустой результат")
            return False
        
        # Тестируем generate_goals
        logger.info("\nТестирую generate_goals...")
        result = server.call_tool("generate_goals", {
            "username": test_username,
            "timeframe": "medium"
        })
        
        if result and result.get('content'):
            logger.info("✅ generate_goals выполнен успешно!")
            logger.info(f"Результат: {result['content'][0]['text'][:200]}...")
        else:
            logger.error("❌ generate_goals вернул пустой результат")
            return False
        
        logger.info("\n🎉 Все тесты прошли успешно!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("=== Тестирование AI Advisor MCP сервера ===")
    
    success = test_ai_advisor()
    
    if success:
        logger.info("✅ Тестирование завершено успешно!")
        sys.exit(0)
    else:
        logger.error("❌ Тестирование завершено с ошибками!")
        sys.exit(1)



