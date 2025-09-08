#!/usr/bin/env python3
"""
AI Advisor MCP Server для работы через STDIO
Возвращает только JSON ответы без тестовой информации
"""

import json
import logging
import os
import sys
from typing import Dict, Any

import openai
from github_client import GitHubClient
from report_generator import ReportGenerator

# Настройка логирования только для ошибок
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class AIAdvisorSTDIOServer:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        self.github_client = GitHubClient(token=os.environ.get('GITHUB_TOKEN'))
        self.report_generator = ReportGenerator(github_client=self.github_client)
        
        # Регистрируем тулсы
        self.tools = {
            "analyze_profile": {
                "name": "analyze_profile",
                "description": "Полный анализ GitHub профиля с AI рекомендациями",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub username для анализа"
                        }
                    },
                    "required": ["username"]
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
                            "name": "ai-advisor",
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
                
                if tool_name == "analyze_profile":
                    username = arguments.get("username", "octocat")
                    result = self.analyze_profile(username)
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

    def analyze_profile(self, username: str) -> str:
        """Анализирует GitHub профиль"""
        try:
            # Получаем профиль пользователя
            profile = self.github_client.get_user_profile_by_username(username)
            if not profile:
                return f"❌ Пользователь {username} не найден"
            
            # Получаем репозитории
            repos = self.github_client.get_user_repositories(username, per_page=100)
            
            # Генерируем отчет
            report = self.report_generator.generate_profile_analysis(profile, repos)
            
            return report
            
        except Exception as e:
            return f"❌ Ошибка анализа профиля: {str(e)}"

def main():
    """Главная функция для работы через STDIO"""
    server = AIAdvisorSTDIOServer()
    
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