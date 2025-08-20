#!/usr/bin/env python3
"""
Python Runner MCP Keepalive Server
Держит STDIO соединение открытым для MCP протокола
"""

import sys
import json
import logging
from typing import Dict, Any, List
from python_runner_mcp_server import PythonRunnerMCPServer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PythonRunnerKeepaliveServer:
    """Keepalive сервер для Python Runner MCP"""
    
    def __init__(self):
        self.mcp_server = PythonRunnerMCPServer()
        logger.info("Python Runner MCP Keepalive Server инициализирован")
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Обрабатывает MCP запрос"""
        method = request.get('method', 'unknown')
        request_id = request.get('id')
        
        logger.info(f"Получен запрос: {method}")
        
        try:
            if method == "initialize":
                tools = self.mcp_server.list_tools()
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {tool["name"]: tool for tool in tools}},
                        "serverInfo": {"name": "Python Runner MCP", "version": "1.0.0"}
                    }
                }
            elif method == "tools/list":
                tools = self.mcp_server.list_tools()
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": tools}
                }
            elif method == "tools/call":
                name = request.get('params', {}).get('name')
                arguments = request.get('params', {}).get('arguments', {})
                result = self.mcp_server.call_tool(name, arguments)
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            elif method == "notifications/initialized":
                logger.info("MCP клиент успешно инициализирован")
                return None
            elif method == "notifications/cancel":
                logger.debug("Получено уведомление об отмене")
                return None
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
            
            return response
            
        except Exception as e:
            logger.error(f"Ошибка обработки запроса {method}: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def run(self):
        """Запускает keepalive STDIO сервер"""
        logger.info("Python Runner MCP сервер запущен")
        
        try:
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
                        request = json.loads(line)
                        response = self.handle_request(request)
                        
                        if response:
                            response_str = json.dumps(response, ensure_ascii=False)
                            print(response_str, flush=True)
                            logger.info(f"Отправлен ответ: {response}")
                    
                    except json.JSONDecodeError as e:
                        logger.error(f"Ошибка парсинга JSON: {e}")
                        continue
                    
                    except Exception as e:
                        logger.error(f"Неожиданная ошибка: {e}")
                        continue
                        
                except KeyboardInterrupt:
                    logger.info("Получен сигнал прерывания, завершение работы")
                    break
                except Exception as e:
                    logger.error(f"Критическая ошибка: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"STDIN закрыт, завершаем работу: {e}")
        finally:
            logger.info("Python Runner MCP сервер завершен")

if __name__ == "__main__":
    server = PythonRunnerKeepaliveServer()
    server.run()
