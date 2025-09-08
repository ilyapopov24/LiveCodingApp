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
    
    def call_mcp_server(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Вызывает MCP сервер через STDIO напрямую или HTTP для Android Two-Agent"""
        try:
            # Android Two-Agent вызывается через ОРИГИНАЛЬНЫЙ 4-агентный сервер
            if server_name == "android-two-agent":
                return self._call_android_two_agent_real(tool_name, arguments)
            
            # Остальные серверы через STDIO
            server_scripts = {
                "github-analytics": "src/github_analytics_stdio_server.py",
                "ai-advisor": "src/ai_advisor_simple_real_stdio_server.py", 
                "python-runner": "src/python_runner_mcp_server.py",
                "ollama": "src/ollama_stdio_server.py",
                "sequential-thinking": "src/sequential_thinking_stdio_server.py",
                "spaceweb": "src/spaceweb_stdio_server.py"
            }
            
            if server_name not in server_scripts:
                return {
                    "success": False,
                    "error": f"Unknown server: {server_name}"
                }
            
            # Создаем MCP запрос
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # Запускаем STDIO сервер
            process = subprocess.Popen(
                ["python", server_scripts[server_name]],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd="/app"
            )
            
            # Отправляем запрос и получаем ответ
            stdout, stderr = process.communicate(
                input=json.dumps(mcp_request, ensure_ascii=False) + "\n",
                timeout=60  # 60 секунд таймаут
            )
            
            if process.returncode != 0:
                logger.error(f"MCP server {server_name} error: {stderr}")
                return {
                    "success": False,
                    "error": f"STDIO error: {stderr}"
                }
            
            # Парсим ответ
            try:
                response = json.loads(stdout.strip())
                
                if "error" in response:
                    return {
                        "success": False,
                        "error": response["error"]["message"]
                    }
                
                # Извлекаем текст из content
                content = response.get("result", {}).get("content", [])
                if content and isinstance(content, list):
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
                    response_text = "\n".join(text_parts) if text_parts else f"{server_name} выполнен успешно"
                else:
                    response_text = f"{server_name} выполнен успешно"
                
                return {
                    "success": True,
                    "data": response.get("result", {}),
                    "response": response_text
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}, stdout: {stdout}")
                return {
                    "success": False,
                    "error": f"JSON parse error: {str(e)}"
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"MCP server {server_name} timeout")
            return {
                "success": False,
                "error": f"Таймаут {server_name}"
            }
        except Exception as e:
            logger.error(f"Error calling MCP server {server_name}: {e}")
            return {
                "success": False,
                "error": f"Ошибка {server_name}: {str(e)}"
            }
    
    def _call_android_two_agent_real(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Вызывает РЕАЛЬНЫЙ Android Two-Agent через STDIO subprocess"""
        try:
            import subprocess
            import json
            
            # Создаем MCP запрос
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # Запускаем ОРИГИНАЛЬНЫЙ 4-агентный сервер через STDIO
            process = subprocess.Popen(
                ["python", "src/real_android_four_agent_mcp_server.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd="/app"
            )
            
            # Отправляем запрос и получаем ответ
            stdout, stderr = process.communicate(
                input=json.dumps(mcp_request, ensure_ascii=False) + "\n",
                timeout=300  # 5 минут таймаут для 4 агентов
            )
            
            if process.returncode != 0:
                logger.error(f"Android Two-Agent REAL error: {stderr}")
                return {
                    "success": False,
                    "error": f"REAL error: {stderr}"
                }
            
            # Парсим ответ - может быть несколько JSON объектов
            try:
                # Разделяем по строкам и берем последний JSON (результат tools/call)
                lines = stdout.strip().split('\n')
                last_json_line = None
                
                for line in lines:
                    if line.strip().startswith('{"jsonrpc":'):
                        last_json_line = line.strip()
                
                if not last_json_line:
                    # Если не нашли jsonrpc, берем последнюю строку
                    last_json_line = lines[-1].strip()
                
                response = json.loads(last_json_line)
                
                if "error" in response:
                    return {
                        "success": False,
                        "error": response["error"]["message"]
                    }
                
                # Извлекаем текст из content
                content = response.get("result", {}).get("content", [])
                if content and isinstance(content, list):
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
                    response_text = "\n".join(text_parts) if text_parts else "Android проект проанализирован 4 агентами"
                else:
                    response_text = "Android проект проанализирован 4 агентами"
                
                return {
                    "success": True,
                    "data": response.get("result", {}),
                    "response": response_text
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}, stdout: {stdout}")
                return {
                    "success": False,
                    "error": f"JSON parse error: {str(e)}"
                }
                
        except subprocess.TimeoutExpired:
            logger.error("Android Two-Agent REAL timeout")
            return {
                "success": False,
                "error": "Таймаут REAL Android Two-Agent (4 агента)"
            }
        except Exception as e:
            logger.error(f"Error calling REAL Android Two-Agent: {e}")
            return {
                "success": False,
                "error": f"Ошибка REAL Android Two-Agent: {str(e)}"
            }

# Создаем экземпляр менеджера
mcp_manager = MCPServerManager()

@app.route('/', methods=['GET'])
def home():
    """Главная страница"""
    return jsonify({
        "service": "MCP HTTP Bridge",
        "version": "1.0.0",
        "endpoints": [
            "/mcp/android-two-agent",
            "/mcp/github-analytics", 
            "/mcp/ai-advisor",
            "/mcp/python-runner",
            "/mcp/sequential-thinking",
            "/mcp/spaceweb"
        ]
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервера"""
    return jsonify({
        "status": "healthy",
        "service": "MCP HTTP Bridge",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/mcp/android-two-agent', methods=['POST'])
def android_two_agent():
    """Эндпоинт для Android Two-Agent MCP сервера"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        logger.info(f"🤖 Android Two-Agent request: {message}")
        
        # Вызываем реальный MCP сервер
        result = mcp_manager.call_mcp_server(
            "android-two-agent",
            "analyze_android_project_with_agents",
            {
                "project_path": "/host"  # Используем правильный путь
            }
        )
        
        if result['success']:
            response_text = result.get('response', 'Android проект проанализирован')
        else:
            response_text = f"❌ Ошибка Android Two-Agent: {result.get('error', 'Неизвестная ошибка')}"
        
        return jsonify({
            "status": "success",
            "response": response_text
        })
    except Exception as e:
        logger.error(f"❌ Error in Android Two-Agent: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/github-analytics', methods=['POST'])
def github_analytics():
    """Эндпоинт для GitHub Analytics MCP сервера"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        logger.info(f"📊 GitHub Analytics request: {message}")
        
        # Извлекаем username из сообщения или используем по умолчанию
        username = "octocat"  # По умолчанию
        if "github.com/" in message or "@" in message:
            # Пытаемся извлечь username из сообщения
            import re
            github_match = re.search(r'github\.com/([a-zA-Z0-9-]+)', message)
            at_match = re.search(r'@([a-zA-Z0-9-]+)', message)
            if github_match:
                username = github_match.group(1)
            elif at_match:
                username = at_match.group(1)
        
        # Вызываем реальный MCP сервер
        result = mcp_manager.call_mcp_server(
            "github-analytics",
            "get_github_profile",
            {"username": username}
        )
        
        if result['success']:
            response_text = result.get('response', 'Анализ GitHub профиля выполнен успешно')
        else:
            response_text = f"❌ Ошибка GitHub Analytics: {result.get('error', 'Неизвестная ошибка')}"
        
        return jsonify({
            "status": "success",
            "response": response_text
        })
    except Exception as e:
        logger.error(f"❌ Error in GitHub Analytics: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/ai-advisor', methods=['POST'])
def ai_advisor():
    """Эндпоинт для AI Advisor MCP сервера"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        logger.info(f"🤖 AI Advisor request: {message}")
        
        # Вызываем реальный MCP сервер
        result = mcp_manager.call_mcp_server(
            "ai-advisor",
            "analyze_profile",
            {"username": "octocat"}  # По умолчанию
        )
        
        if result['success']:
            response_text = result.get('response', 'AI анализ выполнен успешно')
        else:
            response_text = f"❌ Ошибка AI Advisor: {result.get('error', 'Неизвестная ошибка')}"
        
        return jsonify({
            "status": "success",
            "response": response_text
        })
    except Exception as e:
        logger.error(f"❌ Error in AI Advisor: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/python-runner', methods=['POST'])
def python_runner():
    """Эндпоинт для Python Runner MCP сервера"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        logger.info(f"🐍 Python Runner request: {message}")
        
        # Извлекаем путь к файлу из сообщения или используем тестовый файл
        file_path = "/host/test-project/scientific_calculator.py"  # По умолчанию
        if ".py" in message:
            # Пытаемся извлечь путь к файлу из сообщения
            import re
            file_match = re.search(r'([a-zA-Z0-9_/.-]+\.py)', message)
            if file_match:
                file_path = file_match.group(1)
        
        # Вызываем реальный MCP сервер
        result = mcp_manager.call_mcp_server(
            "python-runner",
            "run-python-file",
            {"file_path": file_path}
        )
        
        if result['success']:
            response_text = result.get('response', 'Python код выполнен успешно')
        else:
            response_text = f"❌ Ошибка Python Runner: {result.get('error', 'Неизвестная ошибка')}"
        
        return jsonify({
            "status": "success",
            "response": response_text
        })
    except Exception as e:
        logger.error(f"❌ Error in Python Runner: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/sequential-thinking', methods=['POST'])
def sequential_thinking():
    """Эндпоинт для Sequential Thinking MCP сервера"""
    data = request.get_json()
    message = data.get('message', '')
    
    logger.info(f"🧠 Sequential Thinking request: {message}")
    
    # ВЫЗЫВАЕМ РЕАЛЬНЫЙ Sequential Thinking сервер БЕЗ ЗАГЛУШЕК
    result = mcp_manager.call_mcp_server(
        "sequential-thinking",
        "sequential-thinking",
        {
            "thought": message,
            "next_thought_needed": True,
            "thought_number": 1,
            "total_thoughts": 5
        }
    )
    
    logger.info(f"DEBUG: Sequential Thinking result: {result}")
    
    if result['success']:
        response_text = result.get('response', 'Sequential Thinking выполнен успешно')
    else:
        response_text = f"❌ Ошибка Sequential Thinking: {result.get('error', 'Неизвестная ошибка')}"
    
    return jsonify({
        "status": "success",
        "response": response_text
    })

@app.route('/mcp/spaceweb', methods=['POST'])
def spaceweb():
    """Эндпоинт для Spaceweb MCP сервера"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        logger.info(f"🌐 Spaceweb request: {message}")
        
        # Вызываем реальный MCP сервер
        result = mcp_manager.call_mcp_server(
            "spaceweb",
            "list-vps",
            {}
        )
        
        if result['success']:
            response_text = result.get('response', 'Spaceweb выполнен успешно')
        else:
            response_text = f"❌ Ошибка Spaceweb: {result.get('error', 'Неизвестная ошибка')}"
        
        return jsonify({
            "status": "success",
            "response": response_text
        })
    except Exception as e:
        logger.error(f"❌ Error in Spaceweb: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting HTTP server on {host}:{port}")
    app.run(host=host, port=port, debug=False)