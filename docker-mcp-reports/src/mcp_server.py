#!/usr/bin/env python3
"""
MCP Server for GitHub Analytics and Email Reports
Model Context Protocol server implementation
"""

import asyncio
import json
import logging
import sys
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем существующие модули
from github_client import GitHubClient
from email_sender import EmailSender
from report_generator import ReportGenerator
from config.config import Config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)

class GitHubAnalyticsMCPServer:
    """MCP Server для GitHub аналитики и email отчетов"""
    
    def __init__(self):
        """Инициализация MCP сервера"""
        try:
            self.config = Config()
            self.github_client = GitHubClient(self.config.github_token)
            self.email_sender = EmailSender(self.config)
            self.report_generator = ReportGenerator(self.github_client)
            
            logger.info("MCP Server инициализирован успешно")
        except Exception as e:
            logger.error(f"Ошибка инициализации MCP сервера: {str(e)}")
            raise
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Список доступных tools"""
        logger.info("Запрос списка tools")
        
        tools = [
            {
                "name": "get_github_profile",
                "description": "Получить профиль GitHub пользователя",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub username"
                        }
                    },
                    "required": ["username"]
                }
            },
            {
                "name": "get_github_repositories",
                "description": "Получить список репозиториев GitHub пользователя",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub username"
                        },
                        "max_repos": {
                            "type": "integer",
                            "description": "Максимальное количество репозиториев",
                            "default": 100
                        }
                    },
                    "required": ["username"]
                }
            },
            {
                "name": "get_github_statistics",
                "description": "Получить общую статистику GitHub профиля",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub username"
                        }
                    },
                    "required": ["username"]
                }
            },
            {
                "name": "get_tech_stack_analysis",
                "description": "Анализ технологического стека по языкам программирования",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub username"
                        }
                    },
                    "required": ["username"]
                }
            },
            {
                "name": "generate_github_report",
                "description": "Сгенерировать полный отчет GitHub профиля в Markdown",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub username"
                        }
                    },
                    "required": ["username"]
                }
            },
            {
                "name": "send_github_report",
                "description": "Отправить GitHub отчет по email",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub username"
                        },
                        "recipient_email": {
                            "type": "string",
                            "description": "Email получателя"
                        }
                    },
                    "required": ["username", "recipient_email"]
                }
            },
            {
                "name": "test_email_connection",
                "description": "Протестировать email соединение",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_email_status",
                "description": "Получить статус email конфигурации",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_system_status",
                "description": "Получить статус приложения",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_application_logs",
                "description": "Получить логи приложения",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "lines": {
                            "type": "integer",
                            "description": "Количество строк логов",
                            "default": 100
                        }
                    }
                }
            },
            {
                "name": "validate_configuration",
                "description": "Проверить конфигурацию приложения",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
        
        logger.info(f"Возвращено {len(tools)} tools")
        return tools
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение MCP tool"""
        start_time = datetime.now()
        logger.info(f"Вызов tool: {name} с аргументами: {arguments}")
        
        try:
            result = self._execute_tool(name, arguments)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Tool {name} выполнен успешно за {execution_time:.2f} секунд")
            
            return {"content": [{"type": "text", "text": str(result)}]}
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Ошибка при выполнении tool {name}: {str(e)}"
            logger.error(f"{error_msg} (время выполнения: {execution_time:.2f} сек)")
            
            return {
                "content": [{"type": "text", "text": f"Ошибка: {error_msg}"}]
            }
    
    def _execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Выполнение конкретного tool"""
        if name == "get_github_profile":
            return self._get_github_profile(arguments)
        elif name == "get_github_repositories":
            return self._get_github_repositories(arguments)
        elif name == "get_github_statistics":
            return self._get_github_statistics(arguments)
        elif name == "get_tech_stack_analysis":
            return self._get_tech_stack_analysis(arguments)
        elif name == "generate_github_report":
            return self._generate_github_report(arguments)
        elif name == "send_github_report":
            return self._send_github_report(arguments)
        elif name == "test_email_connection":
            return self._test_email_connection(arguments)
        elif name == "get_email_status":
            return self._get_email_status(arguments)
        elif name == "get_system_status":
            return self._get_system_status(arguments)
        elif name == "get_application_logs":
            return self._get_application_logs(arguments)
        elif name == "validate_configuration":
            return self._validate_configuration(arguments)
        else:
            raise ValueError(f"Неизвестный tool: {name}")
    
    def _get_github_profile(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Получить профиль GitHub пользователя"""
        username = args["username"]
        logger.info(f"Получение профиля GitHub для пользователя: {username}")
        
        profile = self.github_client.get_user_profile_by_username(username)
        if not profile:
            raise Exception(f"Не удалось получить профиль для пользователя {username}")
        
        return {
            "username": profile.get("login"),
            "name": profile.get("name"),
            "bio": profile.get("bio"),
            "company": profile.get("company"),
            "location": profile.get("location"),
            "public_repos": profile.get("public_repos"),
            "followers": profile.get("followers"),
            "following": profile.get("following"),
            "created_at": profile.get("created_at"),
            "updated_at": profile.get("updated_at")
        }
    
    def _get_github_repositories(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить список репозиториев GitHub пользователя"""
        username = args["username"]
        max_repos = args.get("max_repos", 100)
        logger.info(f"Получение репозиториев GitHub для пользователя: {username}, максимум: {max_repos}")
        
        repos = self.github_client.get_user_repositories_by_username(username, max_repos)
        if not repos:
            raise Exception(f"Не удалось получить репозитории для пользователя {username}")
        
        return [
            {
                "name": repo.get("name"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count"),
                "forks": repo.get("forks_count"),
                "size": repo.get("size"),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "url": repo.get("html_url")
            }
            for repo in repos
        ]
    
    def _get_github_statistics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Получить общую статистику GitHub профиля"""
        username = args["username"]
        logger.info(f"Получение статистики GitHub для пользователя: {username}")
        
        profile = self.github_client.get_user_profile_by_username(username)
        repos = self.github_client.get_user_repositories_by_username(username, 1000)
        
        if not profile or not repos:
            raise Exception(f"Not able to get data for user {username}")
        
        total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
        total_forks = sum(repo.get("forks_count", 0) for repo in repos)
        total_size = sum(repo.get("size", 0) for repo in repos)
        
        languages = {}
        for repo in repos:
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        
        return {
            "username": username,
            "total_repositories": len(repos),
            "total_stars": total_stars,
            "total_forks": total_forks,
            "total_size_kb": total_size,
            "languages_count": len(languages),
            "top_languages": dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]),
            "followers": profile.get("followers", 0),
            "following": profile.get("following", 0)
        }
    
    def _get_tech_stack_analysis(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ технологического стека по языкам программирования"""
        username = args["username"]
        logger.info(f"Анализ технологического стека для пользователя: {username}")
        
        repos = self.github_client.get_user_repositories_by_username(username, 1000)
        if not repos:
            raise Exception(f"Не удалось получить репозитории для пользователя {username}")
        
        languages = {}
        for repo in repos:
            lang = repo.get("language")
            if lang:
                if lang not in languages:
                    languages[lang] = {
                        "count": 0,
                        "total_stars": 0,
                        "total_forks": 0,
                        "repositories": []
                    }
                
                languages[lang]["count"] += 1
                languages[lang]["total_stars"] += repo.get("stargazers_count", 0)
                languages[lang]["total_forks"] += repo.get("forks_count", 0)
                languages[lang]["repositories"].append({
                    "name": repo.get("name"),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0)
                })
        
        # Сортируем по количеству репозиториев
        sorted_languages = dict(sorted(languages.items(), key=lambda x: x[1]["count"], reverse=True))
        
        return {
            "username": username,
            "total_languages": len(sorted_languages),
            "languages": sorted_languages,
            "analysis": {
                "most_used": list(sorted_languages.keys())[:5] if sorted_languages else [],
                "most_starred": sorted(sorted_languages.items(), key=lambda x: x[1]["total_stars"], reverse=True)[:5],
                "most_forked": sorted(sorted_languages.items(), key=lambda x: x[1]["total_forks"], reverse=True)[:5]
            }
        }
    
    def _generate_github_report(self, args: Dict[str, Any]) -> str:
        """Сгенерировать полный отчет GitHub профиля в Markdown"""
        username = args["username"]
        logger.info(f"Генерация отчета GitHub для пользователя: {username}")
        
        report = self.report_generator.generate_comprehensive_report(username)
        if not report:
            raise Exception(f"Не удалось сгенерировать отчет для пользователя {username}")
        
        return report
    
    def _send_github_report(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Отправить GitHub отчет по email"""
        username = args["username"]
        recipient_email = args["recipient_email"]
        logger.info(f"Отправка GitHub отчета для пользователя {username} на email: {recipient_email}")
        
        # Генерируем отчет
        report = self.report_generator.generate_comprehensive_report(username)
        if not report:
            raise Exception(f"Не удалось сгенерировать отчет для пользователя {username}")
        
        # Отправляем по email
        subject = f"GitHub Analytics Report - {username} - {datetime.now().strftime('%Y-%m-%d')}"
        success = self.email_sender.send_email(
            subject=subject,
            body=report,
            is_html=False
        )
        
        if success:
            return {
                "status": "success",
                "message": f"Отчет успешно отправлен на {recipient_email}",
                "username": username,
                "recipient_email": recipient_email,
                "subject": subject
            }
        else:
            raise Exception(f"Не удалось отправить отчет на {recipient_email}")
    
    def _test_email_connection(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Протестировать email соединение"""
        logger.info("Тестирование email соединения")
        
        try:
            # Отправляем тестовое письмо
            test_subject = "MCP Server Test Email"
            test_body = f"Это тестовое письмо от MCP сервера. Время: {datetime.now()}"
            
            success = self.email_sender.send_email(
                subject=test_subject,
                body=test_body,
                is_html=False
            )
            
            if success:
                return {
                    "status": "success",
                    "message": "Email соединение работает корректно",
                    "test_time": datetime.now().isoformat()
                }
            else:
                raise Exception("Не удалось отправить тестовое письмо")
                
        except Exception as e:
            raise Exception(f"Ошибка email соединения: {str(e)}")
    
    def _get_email_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Получить статус email конфигурации"""
        logger.info("Получение статуса email конфигурации")
        
        return {
            "email_provider": self.config.email_provider,
            "smtp_server": self.config.smtp_server,
            "smtp_port": self.config.smtp_port,
            "smtp_username": self.config.smtp_username,
            "sender_email": self.config.sender_email,
            "recipient_emails": self.config.recipient_emails,
            "configuration_valid": self.config.is_valid()
        }
    
    def _get_system_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Получить статус приложения"""
        logger.info("Получение статуса системы")
        
        return {
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "github_token_configured": bool(self.config.github_token),
            "email_configured": bool(self.config.smtp_username and self.config.smtp_password),
            "configuration_valid": self.config.is_valid(),
            "version": "1.0.0"
        }
    
    def _get_application_logs(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Получить логи приложения"""
        lines = args.get("lines", 100)
        logger.info(f"Получение {lines} строк логов")
        
        try:
            with open("mcp_server.log", "r", encoding="utf-8") as f:
                log_lines = f.readlines()
            
            # Возвращаем последние N строк
            recent_logs = log_lines[-lines:] if len(log_lines) > lines else log_lines
            
            return {
                "total_lines": len(log_lines),
                "requested_lines": lines,
                "returned_lines": len(recent_logs),
                "logs": recent_logs
            }
        except FileNotFoundError:
            return {
                "total_lines": 0,
                "requested_lines": lines,
                "returned_lines": 0,
                "logs": ["Лог файл не найден"]
            }
    
    def _validate_configuration(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Проверить конфигурацию приложения"""
        logger.info("Проверка конфигурации приложения")
        
        config_status = self.config.is_valid()
        
        return {
            "configuration_valid": config_status,
            "github_token_configured": bool(self.config.github_token),
            "email_configured": bool(self.config.smtp_username and self.config.smtp_password),
            "validation_details": {
                "github": {
                    "token_present": bool(self.config.github_token),
                    "token_length": len(self.config.github_token) if self.config.github_token else 0
                },
                "email": {
                    "smtp_server": bool(self.config.smtp_server),
                    "smtp_port": bool(self.config.smtp_port),
                    "username": bool(self.config.smtp_username),
                    "password": bool(self.config.smtp_password),
                    "sender": bool(self.config.sender_email),
                    "recipients": bool(self.config.recipient_emails)
                }
            }
        }

def main():
    """Главная функция для тестирования MCP сервера"""
    try:
        server = GitHubAnalyticsMCPServer()
        
        # Тестируем список tools
        tools = server.list_tools()
        print(f"Доступно {len(tools)} tools:")
        for tool in tools:
            print(f"- {tool['name']}: {tool['description']}")
        
        # Тестируем системный статус
        status = server.call_tool("get_system_status", {})
        print(f"\nСистемный статус: {status}")
        
        logger.info("MCP Server тестирование завершено успешно")
        
    except Exception as e:
        logger.error(f"Ошибка при тестировании MCP сервера: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
