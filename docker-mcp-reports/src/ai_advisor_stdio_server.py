#!/usr/bin/env python3
"""
STDIO интерфейс для GitHub AI Advisor MCP сервера
"""

import json
import logging
import sys
from typing import Dict, Any

from ai_advisor_mcp_server import GitHubAIAdvisorMCPServer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIAdvisorSTDIOServer:
    def __init__(self):
        self.server = GitHubAIAdvisorMCPServer()
        self.request_id = 0
        
        # Логируем запуск
        logger.info("=== GitHub AI Advisor MCP Server запущен ===")
        logger.info(f"Python версия: {sys.version}")
        logger.info(f"Текущая директория: {sys.path[0]}")
        logger.info(f"Python path: {sys.path}")
        logger.info(f"Доступные тулсы: {[tool['name'] for tool in self.server.list_tools()]}")
    
    def run(self):
        """Основной цикл обработки STDIO"""
        logger.info("Начинаю обработку STDIO...")
        
        try:
            while True:
                # Читаем строку из stdin
                line = sys.stdin.readline()
                if not line:
                    logger.info("stdin закрыт, завершаю работу")
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                logger.info(f"Получен запрос: {line}")
                
                try:
                    # Парсим JSON-RPC запрос
                    request = json.loads(line)
                    response = self.handle_request(request)
                    
                    # Отправляем ответ
                    if response:
                        response_json = json.dumps(response)
                        sys.stdout.write(response_json + '\n')
                        sys.stdout.flush()
                        logger.info(f"Отправлен ответ: {response_json}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Ошибка парсинга JSON: {e}")
                    error_response = self.create_error_response(
                        None, -32700, "Parse error", str(e)
                    )
                    sys.stdout.write(json.dumps(error_response) + '\n')
                    sys.stdout.flush()
                    
                except Exception as e:
                    logger.error(f"Неожиданная ошибка: {e}")
                    error_response = self.create_error_response(
                        None, -32603, "Internal error", str(e)
                    )
                    sys.stdout.write(json.dumps(error_response) + '\n')
                    sys.stdout.flush()
                    
        except KeyboardInterrupt:
            logger.info("Получен сигнал прерывания, завершаю работу")
        except Exception as e:
            logger.error(f"Критическая ошибка в основном цикле: {e}")
        finally:
            logger.info("GitHub AI Advisor MCP Server завершен")
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Обрабатывает JSON-RPC запрос"""
        method = request.get('method')
        request_id = request.get('id')
        params = request.get('params', {})
        
        logger.info(f"Обрабатываю метод: {method}, ID: {request_id}")
        
        try:
            if method == 'initialize':
                return self.handle_initialize(request_id, params)
            elif method == 'tools/list':
                return self.handle_tools_list(request_id)
            elif method == 'tools/call':
                return self.handle_tools_call(request_id, params)
            elif method == 'notifications/initialized':
                return None  # Уведомления не требуют ответа
            elif method == 'notifications/cancel':
                return None  # Уведомления не требуют ответа
            elif method == 'ping':
                return self.create_success_response(request_id, "pong")
            else:
                logger.warning(f"Неизвестный метод: {method}")
                return self.create_error_response(
                    request_id, -32601, "Method not found", f"Unknown method: {method}"
                )
                
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса {method}: {e}")
            return self.create_error_response(
                request_id, -32603, "Internal error", str(e)
            )
    
    def handle_initialize(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Обрабатывает инициализацию"""
        logger.info("Инициализация MCP сервера")
        
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "GitHub AI Advisor",
                    "version": "1.0.0"
                }
            }
        }
        
        logger.info("Инициализация завершена успешно")
        return response
    
    def handle_tools_list(self, request_id: Any) -> Dict[str, Any]:
        """Возвращает список доступных тулсов"""
        logger.info("Запрос списка тулсов")
        
        tools = self.server.list_tools()
        logger.info(f"Найдено {len(tools)} тулсов")
        
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }
        
        return response
    
    def handle_tools_call(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Вызывает указанный тулс"""
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        logger.info(f"Вызов тулса: {tool_name} с аргументами: {arguments}")
        
        try:
            result = self.server.call_tool(tool_name, arguments)
            logger.info(f"Тулс {tool_name} выполнен успешно")
            
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": result.get('content', [])
                }
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Ошибка при выполнении тулса {tool_name}: {e}")
            return self.create_error_response(
                request_id, -32603, "Tool execution error", str(e)
            )
    
    def create_success_response(self, request_id: Any, result: Any) -> Dict[str, Any]:
        """Создает успешный ответ"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
    
    def create_error_response(self, request_id: Any, code: int, message: str, data: str = None) -> Dict[str, Any]:
        """Создает ответ с ошибкой"""
        error_response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
        
        if data:
            error_response["error"]["data"] = data
            
        return error_response


if __name__ == "__main__":
    server = AIAdvisorSTDIOServer()
    server.run()



