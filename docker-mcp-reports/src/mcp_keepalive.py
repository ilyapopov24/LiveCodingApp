#!/usr/bin/env python3
"""
Простой MCP сервер который держит соединение активным
"""

import sys
import json
import logging
from mcp_server import GitHubAnalyticsMCPServer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Главная функция"""
    try:
        logger.info("=== Запуск MCP Keepalive Server ===")
        
        # Создаем MCP сервер
        mcp_server = GitHubAnalyticsMCPServer()
        logger.info("MCP Server создан успешно")
        
        # Простой цикл обработки JSON-RPC
        while True:
            try:
                # Читаем строку из stdin
                line = sys.stdin.readline()
                if not line:
                    logger.info("stdin закрыт, завершаем работу")
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # Парсим JSON запрос
                    request = json.loads(line)
                    method = request.get('method', 'unknown')
                    request_id = request.get('id')
                    
                    logger.info(f"Получен запрос: {method}")
                    
                    # Обрабатываем запрос
                    if method == "initialize":
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {"tools": {}},
                                "serverInfo": {"name": "github-analytics-mcp", "version": "1.0.0"}
                            }
                        }
                    elif method == "tools/list":
                        result = mcp_server.list_tools()
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {"tools": result}
                        }
                    elif method == "tools/call":
                        name = request.get('params', {}).get('name')
                        arguments = request.get('params', {}).get('arguments', {})
                        result = mcp_server.call_tool(name, arguments)
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": result
                        }
                    elif method == "notifications/initialized":
                        logger.info("MCP клиент успешно инициализирован")
                        continue
                    elif method == "notifications/cancel":
                        logger.debug("Получено уведомление об отмене")
                        continue
                    elif method == "ping":
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": "pong"
                        }
                    else:
                        logger.warning(f"Неизвестный метод: {method}")
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32601,
                                "message": f"Method not found: {method}"
                            }
                        }
                    
                    # Отправляем ответ
                    if 'response' in locals():
                        response_json = json.dumps(response, ensure_ascii=False)
                        print(response_json, flush=True)
                        logger.info(f"Отправлен ответ для {method}")
                    
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
                break
            except Exception as e:
                logger.error(f"Критическая ошибка: {str(e)}")
                break
                
    except Exception as e:
        logger.error(f"Ошибка запуска MCP Server: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
    finally:
        logger.info("MCP Keepalive Server завершил работу")

if __name__ == "__main__":
    main()
