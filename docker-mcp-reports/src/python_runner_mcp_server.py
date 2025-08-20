#!/usr/bin/env python3
"""
Python Runner MCP Server
Запускает конкретные Python файлы
"""

import json
import subprocess
import logging
from typing import Dict, Any, List

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PythonRunnerMCPServer:
    """MCP сервер для запуска Python файлов"""
    
    def __init__(self):
        self.tools = [
            {
                "name": "run-python-file",
                "description": "Запускает конкретный Python файл",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Путь к Python файлу для запуска"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        ]
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Возвращает список доступных инструментов"""
        return self.tools
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Вызывает указанный инструмент"""
        if name == "run-python-file":
            return self.run_python_file(arguments)
        else:
            raise ValueError(f"Неизвестный инструмент: {name}")
    
    def run_python_file(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Запускает Python файл"""
        file_path = arguments.get("file_path")
        
        if not file_path:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Ошибка: не указан путь к файлу"
                    }
                ]
            }
        
        try:
            logger.info(f"Запуск Python файла: {file_path}")
            
            # Запускаем Python файл
            result = subprocess.run(
                ["python3", file_path],
                capture_output=True,
                text=True,
                timeout=30  # Таймаут 30 секунд
            )
            
            # Формируем результат
            if result.returncode == 0:
                output = result.stdout.strip()
                logger.info(f"Файл {file_path} выполнен успешно")
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"✅ Файл {file_path} выполнен успешно!\n\n**Вывод:**\n```\n{output}\n```"
                        }
                    ]
                }
            else:
                error_output = result.stderr.strip()
                logger.error(f"Ошибка выполнения файла {file_path}: {error_output}")
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Ошибка выполнения файла {file_path}!\n\n**Код ошибки:** {result.returncode}\n\n**Ошибка:**\n```\n{error_output}\n```"
                        }
                    ]
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"Таймаут выполнения файла {file_path}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"⏰ Таймаут выполнения файла {file_path} (30 секунд)"
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Ошибка запуска файла {file_path}: {str(e)}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"💥 Ошибка запуска файла {file_path}: {str(e)}"
                    }
                ]
            }
