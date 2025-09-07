#!/usr/bin/env python3
"""
Android Two-Agent MCP Keepalive Server
Держит STDIO соединение открытым для MCP протокола
"""

import sys
import json
import logging
import asyncio
from typing import Dict, Any, List
from real_android_two_agent_mcp_server import RealAndroidTwoAgentMCPServer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AndroidTwoAgentKeepaliveServer:
    """Keepalive сервер для Android Two-Agent MCP"""
    
    def __init__(self):
        self.mcp_server = RealAndroidTwoAgentMCPServer()
        logger.info("Android Two-Agent MCP Keepalive Server инициализирован")
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Обрабатывает MCP запрос"""
        method = request.get('method', 'unknown')
        request_id = request.get('id')
        
        logger.info(f"Получен запрос: {method}")
        
        try:
            if method == "initialize":
                tools = self.mcp_server.list_tools()
                
                logger.info(f"Инициализация MCP сервера - доступно тулсов: {len(tools)}")
                for tool in tools:
                    logger.info(f"Тулса: {tool['name']} - {tool['description']}")
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {tool["name"]: tool for tool in tools}},
                        "serverInfo": {"name": "Android Two-Agent MCP", "version": "1.0.0"}
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
                
                logger.info(f"Вызов тулсы: {name} с аргументами: {arguments}")
                
                result = await self.mcp_server.call_tool(name, arguments)
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
                    "result": {"pong": True}
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
            logger.error(f"Ошибка при обработке запроса {method}: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def run(self):
        """Запускает STDIO сервер"""
        logger.info("Android Two-Agent MCP сервер запущен")
        
        try:
            while True:
                line = sys.stdin.readline()
                if not line:
                    break
                
                try:
                    request = json.loads(line.strip())
                    # Создаем новый event loop для каждого запроса
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        response = loop.run_until_complete(self.handle_request(request))
                    finally:
                        loop.close()
                    
                    if response:
                        print(json.dumps(response))
                        sys.stdout.flush()
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Ошибка парсинга JSON: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Неожиданная ошибка: {e}")
                    continue
                    
        except KeyboardInterrupt:
            logger.info("Получен сигнал прерывания, завершение работы")
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
        finally:
            logger.info("Android Two-Agent MCP сервер остановлен")

if __name__ == "__main__":
    server = AndroidTwoAgentKeepaliveServer()
    server.run()