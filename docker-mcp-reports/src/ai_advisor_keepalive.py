#!/usr/bin/env python3
"""
Простой MCP сервер для AI Advisor который держит соединение активным
"""
import sys
import json
import logging
from ai_advisor_mcp_server import GitHubAIAdvisorMCPServer

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # Создаем экземпляр AI Advisor MCP сервера
        server = GitHubAIAdvisorMCPServer()
        
        logger.info("AI Advisor MCP сервер запущен")
        
        # Основной цикл обработки JSON-RPC запросов
        for line in sys.stdin:
            try:
                # Парсим JSON-RPC запрос
                request = json.loads(line.strip())
                
                # Логируем входящий запрос
                logger.info(f"Получен запрос: {request.get('method', 'unknown')}")
                
                # Обрабатываем метод
                method = request.get('method')
                
                if method == 'initialize':
                    # Инициализация
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get('id'),
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {}
                            },
                            "serverInfo": {
                                "name": "github-ai-advisor",
                                "version": "1.0.0"
                            }
                        }
                    }
                    
                elif method == 'tools/list':
                    # Список доступных инструментов
                    tools = server.list_tools()
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get('id'),
                        "result": {
                            "tools": tools
                        }
                    }
                    
                elif method == 'tools/call':
                    # Вызов инструмента
                    tool_name = request['params']['name']
                    arguments = request['params'].get('arguments', {})
                    
                    logger.info(f"Вызываем инструмент: {tool_name} с аргументами: {arguments}")
                    
                    result = server.call_tool(tool_name, arguments)
                    
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get('id'),
                        "result": result
                    }
                    
                elif method == 'notifications/initialized':
                    # Уведомление об инициализации - НЕ отправляем ответ
                    logger.info("Получено уведомление об инициализации")
                    continue
                    
                elif method == 'ping':
                    # Ping для проверки соединения
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get('id'),
                        "result": "pong"
                    }
                    
                else:
                    # Неизвестный метод
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get('id'),
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }
                
                # Отправляем ответ только если есть id
                if 'id' in response:
                    print(json.dumps(response))
                    sys.stdout.flush()
                    logger.info(f"Отправлен ответ: {response.get('result', 'error')}")
                    
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга JSON: {e}")
                continue
            except Exception as e:
                logger.error(f"Ошибка обработки запроса: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get('id') if 'request' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                if error_response.get('id'):
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                    
    except KeyboardInterrupt:
        logger.info("Сервер остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()



