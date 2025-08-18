#!/usr/bin/env python3
"""
MCP STDIO Server for GitHub Analytics
Simple MCP server implementation using STDIO transport
"""

import json
import logging
import sys
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем наш MCP сервер
from mcp_server import GitHubAnalyticsMCPServer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_stdio_server.log'),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)

class MCPSTDIOServer:
    """Простой MCP сервер с STDIO transport"""
    
    def __init__(self):
        """Инициализация MCP сервера"""
        try:
            self.mcp_server = GitHubAnalyticsMCPServer()
            logger.info("MCP STDIO Server инициализирован успешно")
        except Exception as e:
            logger.error(f"Ошибка инициализации MCP STDIO Server: {str(e)}")
            raise
    
    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обработка MCP запроса"""
        try:
            method = request.get("method")
            request_id = request.get("id")
            params = request.get("params", {})
            
            logger.info(f"Обработка запроса: {method} (ID: {request_id})")
            
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "github-analytics-mcp",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                result = self.mcp_server.list_tools()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": result
                    }
                }
            
            elif method == "tools/call":
                name = params.get("name")
                arguments = params.get("arguments", {})
                
                if not name:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": "Missing tool name"
                        }
                    }
                
                result = self.mcp_server.call_tool(name, arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            
            elif method == "notifications/initialized":
                # Успешная инициализация - не возвращаем ответ
                logger.info("MCP клиент успешно инициализирован")
                return None
            
            elif method == "notifications/cancel":
                # Игнорируем уведомления об отмене
                logger.debug("Получено уведомление об отмене")
                return None
            
            elif method == "ping":
                # Простой ping для проверки соединения
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": "pong"
                }
            
            else:
                logger.warning(f"Неизвестный метод: {method}")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Ошибка обработки запроса: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def run(self):
        """Запуск MCP сервера в STDIO режиме"""
        logger.info("Запуск MCP STDIO Server...")
        
        try:
            while True:
                # Читаем строку из stdin
                try:
                    line = sys.stdin.readline()
                    if not line:
                        logger.info("stdin закрыт, завершаем работу")
                        break
                except Exception as e:
                    logger.error(f"Ошибка чтения stdin: {str(e)}")
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # Парсим JSON запрос
                    request = json.loads(line)
                    logger.info(f"Получен запрос: {request.get('method', 'unknown')}")
                    
                    # Обрабатываем запрос
                    response = self.handle_request(request)
                    
                    # Отправляем ответ, если он есть
                    if response:
                        response_json = json.dumps(response, ensure_ascii=False)
                        print(response_json, flush=True)
                        logger.info(f"Отправлен ответ для {request.get('method', 'unknown')}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Ошибка парсинга JSON: {str(e)}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": f"Parse error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                
                except Exception as e:
                    logger.error(f"Неожиданная ошибка: {str(e)}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                    
        except KeyboardInterrupt:
            logger.info("MCP Server остановлен пользователем")
        except Exception as e:
            logger.error(f"Критическая ошибка MCP Server: {str(e)}")
            raise
        finally:
            logger.info("MCP STDIO Server завершил работу")

def main():
    """Главная функция"""
    try:
        logger.info("=== Запуск MCP STDIO Server ===")
        logger.info(f"Python версия: {sys.version}")
        logger.info(f"Текущая директория: {os.getcwd()}")
        logger.info(f"Python path: {sys.path}")
        
        server = MCPSTDIOServer()
        logger.info("MCP Server создан успешно, запускаем основной цикл...")
        server.run()
    except Exception as e:
        logger.error(f"Ошибка запуска MCP STDIO Server: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
