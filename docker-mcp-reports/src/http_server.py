#!/usr/bin/env python3
"""
HTTP сервер как прослойка между Android приложением и MCP серверами
"""

import json
import logging
import os
import subprocess
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для Android приложения

class MCPServerManager:
    """Менеджер для работы с MCP серверами"""
    
    def __init__(self):
        self.project_root = "/app"
    
    def execute_python_runner_command(self, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Выполняет команду в Python Runner MCP сервере"""
        try:
            logger.info(f"Executing Python Runner command: {command} with args: {args}")
            
            # Импортируем и используем Python Runner MCP сервер напрямую
            try:
                from src.python_runner_mcp_server import PythonRunnerMCPServer
                
                # Создаем экземпляр сервера
                server = PythonRunnerMCPServer()
                
                # Вызываем инструмент
                result = server.call_tool(command, args)
                
                logger.info(f"Command executed successfully: {result}")
                return {
                    "success": True,
                    "data": result,
                    "stdout": str(result),
                    "stderr": ""
                }
                
            except ImportError as e:
                logger.error(f"Failed to import PythonRunnerMCPServer: {e}")
                return {
                    "success": False,
                    "error": f"Import error: {e}"
                }
            except Exception as e:
                logger.error(f"Failed to execute command: {e}")
                return {
                    "success": False,
                    "error": f"Execution error: {e}"
                }
                
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {e}"
            }

# Создаем экземпляр менеджера
mcp_manager = MCPServerManager()

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервера"""
    return jsonify({
        "status": "healthy",
        "service": "MCP HTTP Bridge",
        "timestamp": "2025-08-26T23:57:00Z"
    })

@app.route('/fix-android-bug', methods=['POST'])
def fix_android_bug():
    """Эндпоинт для исправления Android багов"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        project_path = data.get('project_path')
        bug_description = data.get('bug_description')
        
        if not project_path or not bug_description:
            return jsonify({
                "success": False,
                "error": "Missing required fields: project_path, bug_description"
            }), 400
        
        logger.info(f"Received fix-android-bug request: project_path={project_path}, bug_description={bug_description}")
        
        # Выполняем команду в Python Runner MCP сервере
        result = mcp_manager.execute_python_runner_command(
            'fix-android-bug',
            {
                'project_path': project_path,
                'bug_description': bug_description
            }
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error in fix-android-bug endpoint: {e}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {e}"
        }), 500

@app.route('/mcp/execute', methods=['POST'])
def execute_mcp_command():
    """Универсальный эндпоинт для выполнения MCP команд"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        tool_name = data.get('tool_name')
        arguments = data.get('arguments', {})
        
        if not tool_name:
            return jsonify({
                "success": False,
                "error": "Missing required field: tool_name"
            }), 400
        
        logger.info(f"Received MCP command: tool_name={tool_name}, arguments={arguments}")
        
        # Выполняем команду в Python Runner MCP сервере
        result = mcp_manager.execute_python_runner_command(tool_name, arguments)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error in execute_mcp_command endpoint: {e}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {e}"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting HTTP server on {host}:{port}")
    app.run(host=host, port=port, debug=False)

