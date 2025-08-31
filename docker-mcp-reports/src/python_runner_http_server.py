#!/usr/bin/env python3
"""
Python Runner HTTP Server
HTTP API для удаленного использования тулс python-runner
"""

import json
import logging
import os
import openai
import anthropic
from typing import Dict, Any
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PythonRunnerHTTPServer:
    """HTTP сервер для запуска Python файлов и генерации тестов"""
    
    def __init__(self):
        # Загружаем переменные окружения
        load_dotenv('docker-settings.env')
        
        # Инициализируем OpenAI клиент
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key or openai_api_key == 'your_openai_api_key_here':
            raise ValueError("OPENAI_API_KEY не настроен в docker.env файле!")
        
        openai.api_key = openai_api_key
        logger.info("OpenAI API настроен успешно")
        
        # Инициализируем Anthropic клиент
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if not anthropic_api_key or anthropic_api_key == 'your_anthropic_api_key_here':
            raise ValueError("ANTHROPIC_API_KEY не настроен в docker.env файле!")
        
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        logger.info("Anthropic API настроен успешно")
        
        # Создаем Flask приложение
        self.app = Flask(__name__)
        CORS(self.app)  # Разрешаем CORS для удаленного доступа
        
        # Регистрируем API endpoints
        self._register_routes()
    
    def _register_routes(self):
        """Регистрирует API endpoints"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Проверка здоровья сервера"""
            return jsonify({
                "status": "healthy",
                "service": "Python Runner HTTP Server",
                "version": "1.0.0"
            })
        
        @self.app.route('/tools', methods=['GET'])
        def list_tools():
            """Список доступных тулс"""
            tools = [
                {
                    "name": "run-python-file",
                    "description": "Запускает конкретный Python файл",
                    "endpoint": "/api/run-python-file"
                },
                {
                    "name": "test-python-code", 
                    "description": "Генерирует и запускает полноценные тесты для Python файла",
                    "endpoint": "/api/test-python-code"
                },
                {
                    "name": "fix-android-bug",
                    "description": "Анализирует Android проект и исправляет указанный баг",
                    "endpoint": "/api/fix-android-bug"
                }
            ]
            return jsonify({"tools": tools})
        
        @self.app.route('/api/run-python-file', methods=['POST'])
        def run_python_file():
            """Запускает конкретный Python файл"""
            try:
                data = request.get_json()
                if not data or 'file_path' not in data:
                    return jsonify({"error": "file_path обязателен"}), 400
                
                file_path = data['file_path']
                logger.info(f"Запуск Python файла: {file_path}")
                
                # Здесь будет логика запуска файла
                result = self._run_python_file(file_path)
                
                return jsonify({
                    "success": True,
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"Ошибка запуска Python файла: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/test-python-code', methods=['POST'])
        def test_python_code():
            """Генерирует и запускает тесты для Python файла"""
            try:
                data = request.get_json()
                if not data or ('file_path' not in data and 'file_content' not in data):
                    return jsonify({"error": "file_path или file_content обязателен"}), 400
                
                if 'file_path' in data:
                    file_path = data['file_path']
                    logger.info(f"Тестирование Python файла по пути: {file_path}")
                    result = self._test_python_code(file_path)
                else:
                    file_content = data['file_content']
                    filename = data.get('filename', 'uploaded_file.py')
                    logger.info(f"Тестирование Python файла по содержимому: {filename}")
                    result = self._test_python_code_content(file_content, filename)
                
                return jsonify({
                    "success": True,
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"Ошибка тестирования Python файла: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/fix-android-bug', methods=['POST'])
        def fix_android_bug():
            """Анализирует Android проект и исправляет баг"""
            try:
                data = request.get_json()
                if not data or 'project_path' not in data or 'bug_description' not in data:
                    return jsonify({"error": "project_path и bug_description обязательны"}), 400
                
                project_path = data['project_path']
                bug_description = data['bug_description']
                logger.info(f"Исправление бага в Android проекте: {project_path}")
                
                # Здесь будет логика исправления бага
                result = self._fix_android_bug(project_path, bug_description)
                
                return jsonify({
                    "success": True,
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"Ошибка исправления бага: {str(e)}")
                return jsonify({"error": str(e)}), 500
    
    def _run_python_file(self, file_path: str) -> Dict[str, Any]:
        """Запускает Python файл"""
        # Заглушка - здесь будет реальная логика
        return {
            "message": f"Файл {file_path} запущен",
            "status": "success"
        }
    
    def _test_python_code(self, file_path: str) -> Dict[str, Any]:
        """Генерирует и запускает тесты через MCP сервер"""
        try:
            # Импортируем MCP сервер
            from python_runner_mcp_server import PythonRunnerMCPServer
            
            # Создаем экземпляр MCP сервера для вызова тулсы
            mcp_server = PythonRunnerMCPServer()
            
            # Вызываем реальную тулсу test-python-code
            result = mcp_server.test_python_code(file_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка генерации тестов: {str(e)}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Ошибка генерации тестов: {str(e)}"
                    }
                ]
            }
    
    def _test_python_code_content(self, file_content: str, filename: str) -> Dict[str, Any]:
        """Генерирует и запускает тесты для содержимого файла"""
        try:
            # Создаем временный файл
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                # Импортируем MCP сервер
                from python_runner_mcp_server import PythonRunnerMCPServer
                
                # Создаем экземпляр MCP сервера для вызова тулсы
                mcp_server = PythonRunnerMCPServer()
                
                # Вызываем реальную тулсу test-python-code с путем к временному файлу
                result = mcp_server.test_python_code(temp_file_path)
                
                return result
                
            finally:
                # Удаляем временный файл
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
            
        except Exception as e:
            logger.error(f"Ошибка генерации тестов для содержимого: {str(e)}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Ошибка генерации тестов: {str(e)}"
                    }
                ]
            }
    
    def _fix_android_bug(self, project_path: str, bug_description: str) -> Dict[str, Any]:
        """Исправляет баг в Android проекте"""
        # Заглушка - здесь будет реальная логика
        return {
            "message": f"Баг в проекте {project_path} исправлен",
            "status": "success"
        }
    
    def run(self, host='0.0.0.0', port=8001):
        """Запускает HTTP сервер"""
        logger.info(f"Запуск Python Runner HTTP сервера на {host}:{port}")
        self.app.run(host=host, port=port, debug=False)

def main():
    """Главная функция"""
    server = PythonRunnerHTTPServer()
    server.run()

if __name__ == "__main__":
    main()
