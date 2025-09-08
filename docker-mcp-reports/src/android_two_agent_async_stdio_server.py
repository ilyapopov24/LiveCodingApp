#!/usr/bin/env python3
"""
STDIO обертка для asyncio Android Two-Agent MCP Server
Запускает оригинальный asyncio сервер в синхронном режиме
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, Any

# Настройка логирования только для ошибок
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Импортируем оригинальный сервер
from real_android_four_agent_mcp_server import RealAndroidFourAgentMCPServer

class AndroidTwoAgentAsyncSTDIOServer:
    def __init__(self):
        self.server = RealAndroidFourAgentMCPServer()
        self.tools = {
            "analyze_android_project_with_agents": {
                "name": "analyze_android_project_with_agents",
                "description": "Analyzes Android project through REAL multi-agent chain",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to Android project"
                        }
                    },
                    "required": ["project_path"]
                }
            }
        }

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Обрабатывает MCP запрос"""
        try:
            method = request.get("method")
            
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "android-two-agent-async-stdio-server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "tools": list(self.tools.values())
                    }
                }
            
            elif method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "analyze_android_project_with_agents":
                    project_path = arguments.get("project_path", "/host")
                    result = self._run_async_analysis(project_path)
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": result
                                }
                            ]
                        }
                    }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

    def _run_async_analysis(self, project_path: str) -> str:
        """Запускает asyncio анализ в синхронном режиме"""
        try:
            # Создаем новый event loop для этого потока
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Запускаем asyncio функцию
                result = loop.run_until_complete(
                    self.server._analyze_android_project_with_agents(project_path)
                )
                
                # Извлекаем текст из результата
                if isinstance(result, dict):
                    if 'content' in result and isinstance(result['content'], list):
                        # Извлекаем текст из content
                        text_parts = []
                        for item in result['content']:
                            if isinstance(item, dict) and 'text' in item:
                                text_parts.append(item['text'])
                        return '\n'.join(text_parts) if text_parts else str(result)
                    else:
                        return str(result)
                else:
                    return str(result)
            finally:
                loop.close()
                
        except Exception as e:
            return f"❌ Ошибка asyncio анализа: {str(e)}"

def main():
    """Главная функция для работы через STDIO"""
    server = AndroidTwoAgentAsyncSTDIOServer()
    
    try:
        # Читаем JSON-RPC запрос из stdin
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
                
            try:
                request = json.loads(line)
                response = server.handle_request(request)
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response, ensure_ascii=False))
                sys.stdout.flush()
                
    except KeyboardInterrupt:
        pass
    except Exception as e:
        error_response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }
        print(json.dumps(error_response, ensure_ascii=False))
        sys.stdout.flush()

if __name__ == "__main__":
    main()
