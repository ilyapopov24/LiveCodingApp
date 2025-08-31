#!/usr/bin/env python3
"""
HTTP сервер как прослойка между Android приложением и MCP серверами
"""

import json
import logging
import os
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
            logger.info(f"🚀 Executing Python Runner command: {command} with args: {args}")
            
            # ПРИНУДИТЕЛЬНЫЙ ВЫВОД В КОНСОЛЬ ДЛЯ DOCKER LOGS
            print(f"🔧 MCP COMMAND: {command}")
            print(f"📝 ARGUMENTS: {args}")
            print(f"⏰ TIMESTAMP: {datetime.now().isoformat()}")
            
            # Импортируем и используем Python Runner MCP сервер напрямую
            try:
                logger.info("📦 Importing PythonRunnerMCPServer...")
                print("📦 Importing PythonRunnerMCPServer...")
                from src.python_runner_mcp_server import PythonRunnerMCPServer
                logger.info("✅ PythonRunnerMCPServer imported successfully")
                print("✅ PythonRunnerMCPServer imported successfully")
                
                # Создаем экземпляр сервера
                logger.info("🔧 Creating server instance...")
                print("🔧 Creating server instance...")
                server = PythonRunnerMCPServer()
                logger.info("✅ Server instance created")
                print("✅ Server instance created")
                
                # Вызываем инструмент
                logger.info(f"🎯 Calling tool: {command}")
                print(f"🎯 Calling tool: {command}")
                result = server.call_tool(command, args)
                logger.info(f"✅ Tool executed successfully")
                print(f"✅ Tool executed successfully")
                logger.info(f"📊 Result type: {type(result)}")
                print(f"📊 Result type: {type(result)}")
                logger.info(f"📄 Result content: {str(result)[:200]}...")
                print(f"📄 Result content: {str(result)[:200]}...")
                
                return {
                    "success": True,
                    "data": result,
                    "stdout": str(result),
                    "stderr": ""
                }
                
            except ImportError as e:
                logger.error(f"❌ Failed to import PythonRunnerMCPServer: {e}")
                logger.error(f"📁 Current working directory: {os.getcwd()}")
                logger.error(f"📂 Directory contents: {os.listdir('.')}")
                return {
                    "success": False,
                    "error": f"Import error: {e}"
                }
            except Exception as e:
                logger.error(f"❌ Failed to execute command: {e}")
                logger.error(f"🔍 Exception type: {type(e)}")
                import traceback
                logger.error(f"📚 Traceback: {traceback.format_exc()}")
                return {
                    "success": False,
                    "error": f"Execution error: {e}"
                }
                
        except Exception as e:
            logger.error(f"💥 Unexpected error: {e}")
            import traceback
            logger.error(f"📚 Traceback: {traceback.format_exc()}")
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
        
        # ПРИНУДИТЕЛЬНЫЙ ВЫВОД В КОНСОЛЬ ДЛЯ DOCKER LOGS
        print(f"🚀 FIX-ANDROID-BUG: project_path={project_path}")
        print(f"🐛 BUG DESCRIPTION: {bug_description}")
        print(f"⏰ TIMESTAMP: {datetime.now().isoformat()}")
        
        # Выполняем команду в Python Runner MCP сервере
        result = mcp_manager.execute_python_runner_command(
            'fix-android-bug',
            {
                'project_path': project_path,
                'bug_description': bug_description
            }
        )
        
        # Логируем результат
        print(f"✅ RESULT: success={result.get('success', False)}")
        if 'error' in result:
            print(f"❌ ERROR: {result['error']}")
        
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

@app.route('/build-android-pipeline', methods=['POST'])
def build_android_pipeline():
    """Эндпоинт для запуска Android debug build pipeline"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        logger.info("Received build-android-pipeline request")
        
        # ПРИНУДИТЕЛЬНЫЙ ВЫВОД В КОНСОЛЬ ДЛЯ DOCKER LOGS
        print(f"🚀 BUILD-ANDROID-PIPELINE: Starting pipeline")
        print(f"⏰ TIMESTAMP: {datetime.now().isoformat()}")
        
        # Выполняем команду в Python Runner MCP сервере
        result = mcp_manager.execute_python_runner_command(
            'build-android-pipeline',
            {}
        )
        
        # Логируем результат
        print(f"✅ RESULT: success={result.get('success', False)}")
        if 'error' in result:
            print(f"❌ ERROR: {result['error']}")
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error in build-android-pipeline endpoint: {e}")
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

