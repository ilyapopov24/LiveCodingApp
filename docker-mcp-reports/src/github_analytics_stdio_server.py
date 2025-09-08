#!/usr/bin/env python3
"""
GitHub Analytics STDIO MCP Server
Реальный сервер для анализа GitHub профилей через STDIO
"""

import json
import sys
import asyncio
import logging
from typing import Dict, Any, List
import requests
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubAnalyticsSTDIOServer:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        self.base_url = "https://api.github.com"
        
    def get_headers(self):
        """Получить заголовки для GitHub API"""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Analytics-MCP-Server/1.0'
        }
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        return headers
    
    def get_github_profile(self, username: str) -> Dict[str, Any]:
        """Получить профиль GitHub пользователя"""
        try:
            url = f"{self.base_url}/users/{username}"
            response = requests.get(url, headers=self.get_headers(), timeout=30)
            
            if response.status_code == 200:
                profile = response.json()
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"👤 **Профиль GitHub: {profile['login']}**\n\n"
                                   f"📝 **Имя:** {profile.get('name', 'Не указано')}\n"
                                   f"📧 **Email:** {profile.get('email', 'Скрыт')}\n"
                                   f"🌍 **Локация:** {profile.get('location', 'Не указана')}\n"
                                   f"🏢 **Компания:** {profile.get('company', 'Не указана')}\n"
                                   f"📊 **Публичные репозитории:** {profile['public_repos']}\n"
                                   f"👥 **Подписчики:** {profile['followers']}\n"
                                   f"👤 **Подписки:** {profile['following']}\n"
                                   f"⭐ **Звезды:** {profile.get('total_private_repos', 0)}\n"
                                   f"📅 **Создан:** {profile['created_at'][:10]}\n"
                                   f"🔄 **Обновлен:** {profile['updated_at'][:10]}\n"
                                   f"📄 **Био:** {profile.get('bio', 'Не указано')}\n"
                                   f"🌐 **Сайт:** {profile.get('blog', 'Не указан')}\n"
                                   f"🐦 **Twitter:** {profile.get('twitter_username', 'Не указан')}"
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Ошибка получения профиля: {response.status_code} - {response.text}"
                        }
                    ]
                }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Ошибка: {str(e)}"
                    }
                ]
            }
    
    def get_github_repositories(self, username: str) -> Dict[str, Any]:
        """Получить список репозиториев GitHub пользователя"""
        try:
            url = f"{self.base_url}/users/{username}/repos"
            response = requests.get(url, headers=self.get_headers(), timeout=30)
            
            if response.status_code == 200:
                repos = response.json()
                repo_list = []
                for repo in repos[:10]:  # Показываем первые 10
                    repo_list.append(f"📁 **{repo['name']}** - {repo.get('description', 'Без описания')}\n"
                                   f"   ⭐ {repo['stargazers_count']} | 🍴 {repo['forks_count']} | "
                                   f"🔧 {repo['language'] or 'Не указан'}")
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"📁 **Репозитории {username}:**\n\n" + "\n\n".join(repo_list)
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Ошибка получения репозиториев: {response.status_code}"
                        }
                    ]
                }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Ошибка: {str(e)}"
                    }
                ]
            }
    
    def get_github_statistics(self, username: str) -> Dict[str, Any]:
        """Получить общую статистику GitHub профиля"""
        try:
            # Получаем профиль
            profile_url = f"{self.base_url}/users/{username}"
            profile_response = requests.get(profile_url, headers=self.get_headers(), timeout=30)
            
            if profile_response.status_code != 200:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Ошибка получения профиля: {profile_response.status_code}"
                        }
                    ]
                }
            
            profile = profile_response.json()
            
            # Получаем репозитории для статистики
            repos_url = f"{self.base_url}/users/{username}/repos"
            repos_response = requests.get(repos_url, headers=self.get_headers(), timeout=30)
            
            if repos_response.status_code == 200:
                repos = repos_response.json()
                
                # Подсчитываем статистику
                total_stars = sum(repo['stargazers_count'] for repo in repos)
                total_forks = sum(repo['forks_count'] for repo in repos)
                languages = {}
                for repo in repos:
                    lang = repo.get('language')
                    if lang:
                        languages[lang] = languages.get(lang, 0) + 1
                
                top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"📊 **Статистика GitHub профиля {username}:**\n\n"
                                   f"📁 **Репозитории:** {profile['public_repos']}\n"
                                   f"⭐ **Общие звезды:** {total_stars}\n"
                                   f"🍴 **Общие форки:** {total_forks}\n"
                                   f"👥 **Подписчики:** {profile['followers']}\n"
                                   f"👤 **Подписки:** {profile['following']}\n"
                                   f"📅 **Активность:** {profile['created_at'][:10]} - {profile['updated_at'][:10]}\n\n"
                                   f"🔧 **Топ языков:**\n" + 
                                   "\n".join([f"   {lang}: {count} репозиториев" for lang, count in top_languages])
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Ошибка получения репозиториев: {repos_response.status_code}"
                        }
                    ]
                }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Ошибка: {str(e)}"
                    }
                ]
            }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Обработать MCP запрос"""
        try:
            method = request.get('method')
            params = request.get('params', {})
            
            if method == 'tools/call':
                tool_name = params.get('name')
                arguments = params.get('arguments', {})
                
                if tool_name == 'get_github_profile':
                    username = arguments.get('username', 'octocat')
                    result = self.get_github_profile(username)
                elif tool_name == 'get_github_repositories':
                    username = arguments.get('username', 'octocat')
                    result = self.get_github_repositories(username)
                elif tool_name == 'get_github_statistics':
                    username = arguments.get('username', 'octocat')
                    result = self.get_github_statistics(username)
                else:
                    result = {
                        "content": [
                            {
                                "type": "text",
                                "text": f"❌ Неизвестный tool: {tool_name}"
                            }
                        ]
                    }
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": result
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get('id'),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

def main():
    """Главная функция STDIO сервера"""
    server = GitHubAnalyticsSTDIOServer()
    
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
                
            try:
                request = json.loads(line)
                response = server.handle_request(request)
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
            except json.JSONDecodeError as e:
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
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    main()

