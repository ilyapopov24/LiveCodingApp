#!/usr/bin/env python3
"""
Упрощенный AI Advisor MCP Server для работы через STDIO
Работает с реальным GitHub API, но без сложной логики
"""

import json
import logging
import os
import sys
from typing import Dict, Any

import openai
import requests

# Настройка логирования только для ошибок
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class SimpleRealAIAdvisorSTDIOServer:
    def __init__(self):
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        
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
                            "name": "simple-real-ai-advisor",
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

    def get_github_profile(self, username: str) -> Dict[str, Any]:
        """Получает профиль пользователя с GitHub API"""
        try:
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(f'https://api.github.com/users/{username}', headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            return None

    def get_github_repos(self, username: str) -> list:
        """Получает репозитории пользователя с GitHub API"""
        try:
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(f'https://api.github.com/users/{username}/repos?per_page=100', headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        except Exception as e:
            return []

    def analyze_profile(self, username: str) -> str:
        """Анализирует GitHub профиль с реальным API"""
        try:
            # Получаем реальный профиль пользователя
            profile = self.get_github_profile(username)
            if not profile:
                return f"❌ Пользователь {username} не найден или ошибка API"
            
            # Получаем реальные репозитории
            repos = self.get_github_repos(username)
            
            # Простой анализ без OpenAI
            public_repos = len(repos)
            total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
            total_forks = sum(repo.get('forks_count', 0) for repo in repos)
            
            # Определяем основные языки
            languages = {}
            for repo in repos:
                lang = repo.get('language')
                if lang:
                    languages[lang] = languages.get(lang, 0) + 1
            
            top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Формируем отчет
            report = f"""🤖 **Анализ профиля GitHub: @{username}**

## 📊 Реальные данные:
- **Имя**: {profile.get('name', 'N/A')}
- **Био**: {profile.get('bio', 'N/A')}
- **Компания**: {profile.get('company', 'N/A')}
- **Локация**: {profile.get('location', 'N/A')}
- **Публичные репозитории**: {public_repos}
- **Общее количество звезд**: {total_stars}
- **Общее количество форков**: {total_forks}
- **Подписчики**: {profile.get('followers', 0)}
- **Подписки**: {profile.get('following', 0)}

## 🔧 Технологический стек:
"""
            
            for lang, count in top_languages:
                report += f"- **{lang}**: {count} репозиториев\n"
            
            report += f"""
## 📈 Рекомендации:
1. **Активность**: {'✅ Высокая' if public_repos > 10 else '⚠️ Низкая'} активность
2. **Популярность**: {'✅ Высокая' if total_stars > 100 else '⚠️ Низкая'} популярность
3. **Сообщество**: {'✅ Активное' if total_forks > 50 else '⚠️ Пассивное'} сообщество

## 🎯 План развития:
- Увеличить количество публичных репозиториев
- Улучшить документацию в README файлах
- Добавить больше тестов в проекты
- Участвовать в open source сообществе
"""
            
            return report
            
        except Exception as e:
            return f"❌ Ошибка анализа профиля: {str(e)}"

def main():
    """Главная функция для работы через STDIO"""
    server = SimpleRealAIAdvisorSTDIOServer()
    
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

