#!/usr/bin/env python3
"""
HTTP версия Android Two-Agent MCP Server
Работает через HTTP API как оригинальный сервер
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
from real_android_four_agent_mcp_server import RealAndroidFourAgentMCPServer
from flask import Flask, request, jsonify

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Глобальный экземпляр сервера
android_agent_server = None

def init_server():
    """Инициализация сервера"""
    global android_agent_server
    if android_agent_server is None:
        android_agent_server = RealAndroidFourAgentMCPServer()
        logger.info("Android Two-Agent HTTP Server инициализирован")

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервера"""
    return jsonify({"status": "healthy", "service": "android-two-agent-http"})

@app.route('/mcp', methods=['POST'])
def mcp_endpoint():
    """Основной MCP эндпоинт"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        method = data.get("method")
        
        if method == "initialize":
            return jsonify({
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "android-two-agent-http-server",
                        "version": "1.0.0"
                    }
                }
            })
        
        elif method == "tools/list":
            tools = android_agent_server.list_tools()
            return jsonify({
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "result": {
                    "tools": tools
                }
            })
        
        elif method == "tools/call":
            params = data.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            # Запускаем asyncio функцию
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    android_agent_server.call_tool(tool_name, arguments)
                )
                return jsonify(result)
            finally:
                loop.close()
        
        else:
            return jsonify({
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Unknown method: {method}"
                }
            }), 400
            
    except Exception as e:
        logger.error(f"Error in MCP endpoint: {e}")
        return jsonify({
            "jsonrpc": "2.0",
            "id": data.get("id") if 'data' in locals() else None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_endpoint():
    """Упрощенный эндпоинт для анализа Android проекта"""
    try:
        data = request.get_json()
        project_path = data.get("project_path", "/host")
        
        logger.info(f"🤖 Android Two-Agent HTTP request: {project_path}")
        
        # Запускаем asyncio функцию
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                android_agent_server._analyze_android_project_with_agents(project_path)
            )
            
            # Извлекаем текст из результата
            if isinstance(result, dict) and 'content' in result:
                content = result['content']
                if isinstance(content, list):
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and 'text' in item:
                            text_parts.append(item['text'])
                    response_text = '\n'.join(text_parts) if text_parts else str(result)
                else:
                    response_text = str(content)
            else:
                response_text = str(result)
            
            return jsonify({
                "success": True,
                "response": response_text,
                "data": result
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {e}")
        return jsonify({
            "success": False,
            "error": f"Ошибка Android Two-Agent: {str(e)}"
        }), 500

if __name__ == "__main__":
    init_server()
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting Android Two-Agent HTTP Server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)

