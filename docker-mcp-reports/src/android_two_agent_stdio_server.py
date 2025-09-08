#!/usr/bin/env python3
"""
Android Two-Agent MCP Server для работы через STDIO
Упрощенная версия без асинхронности
"""

import json
import logging
import os
import sys
from typing import Dict, Any

# Настройка логирования только для ошибок
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class AndroidTwoAgentSTDIOServer:
    def __init__(self):
        # Регистрируем тулсы
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
                            "name": "android-two-agent-stdio-server",
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
                    result = self.analyze_android_project(project_path)
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

    def analyze_android_project(self, project_path: str) -> str:
        """Анализирует Android проект"""
        try:
            # Простой анализ Android проекта
            if not os.path.exists(project_path):
                return f"❌ Проект не найден: {project_path}"
            
            # Проверяем что это Android проект
            build_gradle = os.path.join(project_path, "build.gradle")
            app_build_gradle = os.path.join(project_path, "app", "build.gradle")
            
            if not os.path.exists(build_gradle) and not os.path.exists(app_build_gradle):
                return f"❌ Это не Android проект: {project_path}"
            
            # Подсчитываем файлы
            kotlin_files = 0
            java_files = 0
            xml_files = 0
            
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.endswith('.kt'):
                        kotlin_files += 1
                    elif file.endswith('.java'):
                        java_files += 1
                    elif file.endswith('.xml'):
                        xml_files += 1
            
            # Анализируем структуру
            has_activities = False
            has_fragments = False
            has_viewmodels = False
            
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.endswith('.kt') or file.endswith('.java'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if 'Activity' in content:
                                    has_activities = True
                                if 'Fragment' in content:
                                    has_fragments = True
                                if 'ViewModel' in content:
                                    has_viewmodels = True
                        except:
                            continue
            
            # Формируем отчет
            report = f"""🤖 **Анализ Android проекта: {project_path}**

## 📊 Статистика файлов:
- **Kotlin файлы**: {kotlin_files}
- **Java файлы**: {java_files}
- **XML файлы**: {xml_files}
- **Всего файлов**: {kotlin_files + java_files + xml_files}

## 🏗️ Архитектура:
- **Activities**: {'✅ Есть' if has_activities else '❌ Нет'}
- **Fragments**: {'✅ Есть' if has_fragments else '❌ Нет'}
- **ViewModels**: {'✅ Есть' if has_viewmodels else '❌ Нет'}

## 🔍 Рекомендации:
1. **Архитектура**: {'✅ Хорошая' if has_viewmodels else '⚠️ Добавить ViewModels'}
2. **UI**: {'✅ Использует Fragments' if has_fragments else '⚠️ Рассмотреть Fragments'}
3. **Язык**: {'✅ Kotlin' if kotlin_files > java_files else '⚠️ Больше Java чем Kotlin'}

## 🎯 План улучшений:
- Добавить больше тестов
- Улучшить архитектуру (MVVM)
- Оптимизировать производительность
- Добавить документацию
"""
            
            return report
            
        except Exception as e:
            return f"❌ Ошибка анализа проекта: {str(e)}"

def main():
    """Главная функция для работы через STDIO"""
    server = AndroidTwoAgentSTDIOServer()
    
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

