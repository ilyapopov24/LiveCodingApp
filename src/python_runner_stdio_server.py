#!/usr/bin/env python3
"""
STDIO сервер для Python Runner MCP
"""

import json
import logging
import sys
from python_runner_mcp_server import PythonRunnerMCPServer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PythonRunnerSTDIOServer:
    """STDIO сервер для Python Runner MCP"""
    
    def __init__(self):
        self.mcp_server = PythonRunnerMCPServer()
        self.initialized = False
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Обрабатывает входящий запрос"""
        method = request.get("method")
        request_id = request.get("id")
        
        logger.info(f"Получен запрос: {method}")
        
        if method == "initialize":
            self.initialized = True
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "Python Runner MCP",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            if not self.initialized:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32002,
                        "message": "Сервер не инициализирован"
                    }
                }
            
            tools = self.mcp_server.list_tools()
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": tools
                }
            }
        
        elif method == "tools/call":
            if not self.initialized:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32002,
                        "message": "Сервер не инициализирован"
                    }
                }
            
            params = request.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            try:
                result = self.mcp_server.call_tool(tool_name, arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            except Exception as e:
                logger.error(f"Ошибка при выполнении тулса {tool_name}: {e}")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"Внутренняя ошибка: {str(e)}"
                    }
                }
        
        elif method == "notifications/initialized":
            # Уведомления не требуют ответа
            return None
        
        elif method == "ping":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": "pong"
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Метод {method} не найден"
                }
            }
    
    def run(self):
        """Запускает STDIO сервер"""
        logger.info("Python Runner MCP сервер запущен")
        
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
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

if __name__ == "__main__":
    server = PythonRunnerSTDIOServer()
    server.run()
