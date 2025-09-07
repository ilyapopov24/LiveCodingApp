#!/usr/bin/env python3
"""
Real Android Two-Agent MCP Server
MCP сервер для НАСТОЯЩЕЙ мультиагентной системы из 2 агентов
"""

import asyncio
import json
import logging
import sys
import os
from typing import Any, Dict, List, Optional
from real_android_two_agent_system import RealAndroidTwoAgentSystem

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_android_two_agent_mcp_server.log'),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)

class RealAndroidTwoAgentMCPServer:
    """MCP Server для НАСТОЯЩЕЙ мультиагентной системы из 2 агентов"""
    
    def __init__(self):
        self.two_agent_system = RealAndroidTwoAgentSystem()
        logger.info("Real Android Two-Agent MCP Server инициализирован")
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Список доступных tools"""
        return [
            {
                "name": "analyze_android_project_with_agents",
                "description": "Analyzes Android project through REAL multi-agent chain: Code Analyzer → Bug Detector",
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
            },
            {
                "name": "get_agent_decisions",
                "description": "Gets decisions made by agents",
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
            },
            {
                "name": "get_inter_agent_communication",
                "description": "Gets inter-agent communication log",
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
            },
            {
                "name": "get_agent_chain_info",
                "description": "Gets information about agent chain",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "send_message_to_agent",
                "description": "Sends message to specific agent",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "enum": ["code_analyzer", "bug_detector"],
                            "description": "Agent name"
                        },
                        "message_type": {
                            "type": "string",
                            "description": "Message type"
                        },
                        "data": {
                            "type": "object",
                            "description": "Message data"
                        }
                    },
                    "required": ["agent_name", "message_type", "data"]
                }
            },
            {
                "name": "broadcast_message_to_agents",
                "description": "Sends message to all agents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message_type": {
                            "type": "string",
                            "description": "Message type"
                        },
                        "data": {
                            "type": "object",
                            "description": "Message data"
                        }
                    },
                    "required": ["message_type", "data"]
                }
            }
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Вызывает указанный tool"""
        try:
            logger.info(f"Вызов tool: {tool_name} с аргументами: {arguments}")
            
            if tool_name == "analyze_android_project_with_agents":
                return await self._analyze_android_project_with_agents(arguments.get('project_path'))
            
            elif tool_name == "get_agent_decisions":
                return await self._get_agent_decisions(arguments.get('project_path'))
            
            elif tool_name == "get_inter_agent_communication":
                return await self._get_inter_agent_communication(arguments.get('project_path'))
            
            elif tool_name == "get_agent_chain_info":
                return await self._get_agent_chain_info()
            
            elif tool_name == "send_message_to_agent":
                return await self._send_message_to_agent(
                    arguments.get('agent_name'),
                    arguments.get('message_type'),
                    arguments.get('data')
                )
            
            elif tool_name == "broadcast_message_to_agents":
                return await self._broadcast_message_to_agents(
                    arguments.get('message_type'),
                    arguments.get('data')
                )
            
            else:
                return {
                    "error": f"Неизвестный tool: {tool_name}",
                    "available_tools": [tool["name"] for tool in self.list_tools()]
                }
                
        except Exception as e:
            logger.error(f"Ошибка при вызове tool {tool_name}: {str(e)}")
            return {
                "error": str(e),
                "tool": tool_name,
                "arguments": arguments
            }
    
    async def _analyze_android_project_with_agents(self, project_path: str) -> Dict[str, Any]:
        """Анализирует Android проект через НАСТОЯЩУЮ мультиагентную цепочку"""
        if not project_path:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "❌ Путь к проекту не указан"
                    }
                ]
            }
        
        try:
            result = await self.two_agent_system.process_android_project(project_path)
            
            # Форматируем результат для отображения
            bugs = result.get('chain_result', {}).get('all_bugs', [])
            total_bugs = len(bugs)
            
            output_text = f"🤖 **Анализ Android проекта завершен**\n\n"
            output_text += f"📁 **Проект:** {project_path}\n"
            output_text += f"🐛 **Найдено багов:** {total_bugs}\n\n"
            
            if bugs:
                output_text += "**Найденные проблемы:**\n"
                for i, bug in enumerate(bugs, 1):
                    severity = bug.get('severity', 'unknown')
                    file_path = bug.get('file', 'unknown')
                    description = bug.get('description', 'No description')
                    output_text += f"{i}. **{severity.upper()}** - `{file_path}`\n   {description}\n\n"
            else:
                output_text += "✅ **Проблем не найдено!**\n\n"
            
            # Добавляем информацию о решениях агентов
            agent_decisions = result.get('agent_decisions', {})
            if agent_decisions:
                output_text += "**Решения агентов:**\n"
                for agent, decisions in agent_decisions.items():
                    output_text += f"- **{agent}:** {len(decisions)} решений\n"
                output_text += "\n"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": output_text
                    }
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"💥 **Ошибка анализа проекта {project_path}:**\n{str(e)}"
                    }
                ]
            }
    
    async def _get_agent_decisions(self, project_path: str) -> Dict[str, Any]:
        """Получает решения агентов"""
        if not project_path:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "❌ Путь к проекту не указан"
                    }
                ]
            }
        
        try:
            # Сначала запускаем анализ
            result = await self.two_agent_system.process_android_project(project_path)
            decisions = result.get('agent_decisions', {})
            
            output_text = f"🤖 **Решения агентов для проекта {project_path}**\n\n"
            
            total_decisions = sum(len(decisions.get(agent, [])) for agent in decisions)
            output_text += f"📊 **Всего решений:** {total_decisions}\n\n"
            
            for agent, agent_decisions in decisions.items():
                output_text += f"**{agent}:**\n"
                for decision in agent_decisions:
                    timestamp = decision.get('timestamp', 'unknown')
                    decision_type = decision.get('decision', 'unknown')
                    value = decision.get('value', 'unknown')
                    reasoning = decision.get('reasoning', 'No reasoning provided')
                    output_text += f"- **{decision_type}:** {value}\n  *{reasoning}*\n"
                output_text += "\n"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": output_text
                    }
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"💥 **Ошибка получения решений агентов для проекта {project_path}:**\n{str(e)}"
                    }
                ]
            }
    
    async def _get_inter_agent_communication(self, project_path: str) -> Dict[str, Any]:
        """Получает лог меж-агентного общения"""
        if not project_path:
            return {"error": "Путь к проекту не указан"}
        
        try:
            # Сначала запускаем анализ
            result = await self.two_agent_system.process_android_project(project_path)
            communication = result.get('inter_agent_communication', [])
            
            return {
                "success": True,
                "inter_agent_communication": communication,
                "message": f"Получен лог меж-агентного общения для проекта {project_path}",
                "total_messages": len(communication)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Ошибка при получении лога общения для проекта {project_path}"
            }
    
    async def _get_agent_chain_info(self) -> Dict[str, Any]:
        """Получает информацию о цепочке агентов"""
        try:
            chain_info = await self.two_agent_system.get_agent_chain_info()
            agent_status = await self.two_agent_system.get_agent_status()
            
            return {
                "success": True,
                "chain_info": chain_info,
                "agent_status": agent_status,
                "message": "Информация о цепочке агентов получена"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Ошибка при получении информации о цепочке агентов"
            }
    
    async def _send_message_to_agent(self, agent_name: str, message_type: str, data: Any) -> Dict[str, Any]:
        """Отправляет сообщение конкретному агенту"""
        try:
            self.two_agent_system.send_message_to_agent(agent_name, message_type, data)
            
            return {
                "success": True,
                "message": f"Сообщение {message_type} отправлено агенту {agent_name}",
                "agent_name": agent_name,
                "message_type": message_type
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Ошибка при отправке сообщения агенту {agent_name}"
            }
    
    async def _broadcast_message_to_agents(self, message_type: str, data: Any) -> Dict[str, Any]:
        """Отправляет сообщение всем агентам"""
        try:
            await self.two_agent_system.broadcast_message(message_type, data)
            
            return {
                "success": True,
                "message": f"Сообщение {message_type} отправлено всем агентам",
                "message_type": message_type,
                "recipients": ["code_analyzer", "bug_detector"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Ошибка при отправке сообщения всем агентам"
            }
    
    async def initialize(self) -> Dict[str, Any]:
        """Инициализация MCP сервера"""
        try:
            tools = self.list_tools()
            capabilities = {
                "tools": {tool["name"]: tool for tool in tools}
            }
            
            logger.info("Real Android Two-Agent MCP Server инициализирован успешно")
            return {
                "protocolVersion": "2024-11-05",
                "capabilities": capabilities,
                "serverInfo": {
                    "name": "real-android-two-agent-mcp-server",
                    "version": "1.0.0",
                    "description": "MCP сервер для НАСТОЯЩЕЙ мультиагентной системы Android разработки (2 агента с принятием решений)"
                }
            }
        except Exception as e:
            logger.error(f"Ошибка инициализации MCP сервера: {str(e)}")
            raise

# Основная функция для запуска MCP сервера
async def main():
    """Главная функция для запуска MCP сервера"""
    server = RealAndroidTwoAgentMCPServer()
    
    # Инициализация
    init_result = await server.initialize()
    print(json.dumps(init_result))
    
    # Основной цикл обработки сообщений
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            message = json.loads(line.strip())
            
            if message.get("method") == "tools/call":
                tool_name = message.get("params", {}).get("name")
                arguments = message.get("params", {}).get("arguments", {})
                
                result = await server.call_tool(tool_name, arguments)
                
                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, ensure_ascii=False, indent=2)
                            }
                        ]
                    }
                }
                
                print(json.dumps(response))
                
            elif message.get("method") == "tools/list":
                tools = server.list_tools()
                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": {
                        "tools": tools
                    }
                }
                print(json.dumps(response))
                
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
