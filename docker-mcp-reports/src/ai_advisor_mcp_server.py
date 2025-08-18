import json
import logging
import os
import subprocess
from typing import Dict, Any, List

import openai
from github_client import GitHubClient
from report_generator import ReportGenerator

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubAIAdvisorMCPServer:
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
            },
            "suggest_improvements": {
                "name": "suggest_improvements",
                "description": "Конкретные улучшения для GitHub профиля",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub username для анализа"
                        },
                        "focus_area": {
                            "type": "string",
                            "enum": ["repos", "profile", "activity", "overall"],
                            "description": "Область для фокуса улучшений"
                        }
                    },
                    "required": ["username", "focus_area"]
                }
            },
            "generate_goals": {
                "name": "generate_goals",
                "description": "Генерация целей для развития на основе текущего профиля",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub username для анализа"
                        },
                        "timeframe": {
                            "type": "string",
                            "enum": ["short", "medium", "long"],
                            "description": "Временной горизонт для целей"
                        }
                    },
                    "required": ["username", "timeframe"]
                }
            },
            "compare_with_peers": {
                "name": "compare_with_peers",
                "description": "Сравнение профиля с похожими профилями",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub username для анализа"
                        },
                        "peer_usernames": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Список username для сравнения"
                        }
                    },
                    "required": ["username", "peer_usernames"]
                }
            }
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Возвращает список доступных тулсов"""
        return [
            {
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
            },
            {
                "name": "analyze_profile_with_analytics",
                "description": "Комбинированный анализ: GitHub Analytics + AI Advisor (показывает работу обоих MCP серверов)",
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
            },
            {
                "name": "suggest_improvements",
                "description": "Конкретные улучшения для GitHub профиля",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub username для анализа"
                        },
                        "focus_area": {
                            "type": "string",
                            "enum": ["repos", "profile", "activity", "overall"],
                            "description": "Область для фокуса улучшений"
                        }
                    },
                    "required": ["username", "focus_area"]
                }
            },
            {
                "name": "generate_goals",
                "description": "Генерация целей для развития на основе текущего профиля",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub username для анализа"
                        },
                        "timeframe": {
                            "type": "string",
                            "enum": ["short", "medium", "long"],
                            "description": "Временной горизонт для целей"
                        }
                    },
                    "required": ["username", "timeframe"]
                }
            },
            {
                "name": "compare_with_peers",
                "description": "Сравнение профиля с похожими профилями",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub username для анализа"
                        },
                        "peer_usernames": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Список username для сравнения"
                        }
                    },
                    "required": ["username", "peer_usernames"]
                }
            }
        ]
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Вызывает указанный тулс с аргументами"""
        logger.info(f"Вызываю тулс: {tool_name} с аргументами: {arguments}")
        
        try:
            if tool_name == "analyze_profile":
                result = self._analyze_profile(arguments["username"])
            elif tool_name == "analyze_profile_with_analytics":
                result = self._analyze_profile_with_analytics(arguments["username"])
            elif tool_name == "suggest_improvements":
                result = self._suggest_improvements(arguments["username"], arguments["focus_area"])
            elif tool_name == "generate_goals":
                result = self._generate_goals(arguments["username"], arguments["timeframe"])
            elif tool_name == "compare_with_peers":
                result = self._compare_with_peers(arguments["username"], arguments["peer_usernames"])
            else:
                raise ValueError(f"Неизвестный тулс: {tool_name}")
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Ошибка при вызове тулса {tool_name}: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Ошибка при выполнении {tool_name}: {str(e)}"
                    }
                ]
            }
    
    def _analyze_profile(self, username: str) -> str:
        """Полный анализ профиля"""
        logger.info(f"Начинаю анализ профиля для {username}")
        
        # Получаем данные через первый MCP (симулируем вызов)
        profile_data = self._get_profile_data(username)
        
        # Формируем промпт для OpenAI
        prompt = f"Проанализируй следующий GitHub профиль и дай комплексные рекомендации по улучшению:\n\n{profile_data}\n\nЗадача: Оцени текущее состояние профиля и предложи конкретные улучшения по:\n1. Профилю и био\n2. Репозиториям и качеству кода\n3. Активности и вкладу в сообщество\n4. Технологическому стеку\n5. Документации и README\n\nФормат ответа: Markdown с:\n- Кратким анализом текущего состояния\n- Приоритетными областями для улучшения\n- Конкретными рекомендациями по каждому пункту\n- Планом действий на ближайшие 3 месяца"
        
        return self._get_openai_analysis(prompt)
    
    def _analyze_profile_with_analytics(self, username: str) -> str:
        """Комбинированный анализ: показывает работу обоих MCP серверов"""
        logger.info(f"Комбинированный анализ профиля: {username}")
        
        # Шаг 1: Получаем данные через GitHub Analytics MCP (симулируем)
        logger.info("=== ШАГ 1: Получение данных через GitHub Analytics MCP ===")
        try:
            # Получаем профиль
            profile = self.github_client.get_user_profile_by_username(username)
            logger.info(f"✅ GitHub Analytics MCP: получен профиль для {username}")
            
            # Получаем репозитории
            repos = self.github_client.get_user_repositories_by_username(username, per_page=100)
            logger.info(f"✅ GitHub Analytics MCP: получено {len(repos)} репозиториев")
            
            # Статистика уже доступна в профиле
            logger.info(f"✅ GitHub Analytics MCP: статистика получена из профиля")
            
        except Exception as e:
            logger.error(f"❌ GitHub Analytics MCP: ошибка при получении данных: {e}")
            return f"Ошибка при получении данных через GitHub Analytics MCP: {str(e)}"
        
        # Шаг 2: AI анализ через AI Advisor MCP
        logger.info("=== ШАГ 2: AI анализ через AI Advisor MCP ===")
        
        # Формируем структурированные данные для AI
        profile_data = f"## Профиль пользователя: {username}\n\n### Основная информация:\n- Имя: {profile.get('name', 'Не указано')}\n- Bio: {profile.get('bio', 'Не указано')}\n- Компания: {profile.get('company', 'Не указано')}\n- Локация: {profile.get('location', 'Не указано')}\n- Сайт: {profile.get('blog', 'Не указано')}\n- Twitter: {profile.get('twitter_username', 'Не указано')}\n\n### Статистика:\n- Публичных репозиториев: {profile.get('public_repos', 0)}\n- Публичных gists: {profile.get('public_gists', 0)}\n- Подписчиков: {profile.get('followers', 0)}\n- Подписок: {profile.get('following', 0)}\n- Дата создания: {profile.get('created_at', 'Не указано')}\n- Последняя активность: {profile.get('updated_at', 'Не указано')}\n\n### Репозитории (топ 10 по звездам):"
        
        # Добавляем топ репозитории
        sorted_repos = sorted(repos, key=lambda x: x.get('stargazers_count', 0), reverse=True)
        for repo in sorted_repos[:10]:
            repo_name = repo['name']
            repo_desc = repo.get('description', 'Без описания')
            repo_lang = repo.get('language', 'Не указан')
            repo_stars = repo.get('stargazers_count', 0)
            repo_forks = repo.get('forks_count', 0)
            repo_size = repo.get('size', 0)
            repo_updated = repo.get('updated_at', 'Не указано')
            
            profile_data += f"\n- {repo_name}: {repo_desc}\n  - Язык: {repo_lang}\n  - Звезды: {repo_stars}\n  - Форки: {repo_forks}\n  - Размер: {repo_size} KB\n  - Последнее обновление: {repo_updated}"
        
        prompt = f"""Анализирую GitHub профиль с использованием двух MCP серверов:

🔍 **GitHub Analytics MCP** (уже выполнен):
- Собрал данные профиля
- Получил список репозиториев  
- Собрал статистику активности

🤖 **AI Advisor MCP** (выполняется сейчас):
- Анализирую собранные данные
- Генерирую рекомендации

Данные профиля:
{profile_data}

Задача: Дай подробный анализ и рекомендации, подчеркивая, что использовались оба MCP сервера.

Формат ответа:
1. Краткое резюме профиля
2. Анализ сильных сторон
3. Области для улучшения
4. Конкретные рекомендации
5. План развития

В конце обязательно укажи: "✅ Анализ выполнен с использованием GitHub Analytics MCP + AI Advisor MCP" """

        logger.info("✅ AI Advisor MCP: отправляю данные в OpenAI для анализа")
        return self._get_openai_analysis(prompt)
    
    def _suggest_improvements(self, username: str, focus_area: str) -> str:
        """Конкретные улучшения для определенной области"""
        logger.info(f"Анализирую улучшения для {username} в области {focus_area}")
        
        profile_data = self._get_profile_data(username)
        
        focus_prompts = {
            "repos": "Оцени качество кода в репозиториях и предложи улучшения по структуре, тестированию, документации",
            "profile": "Проанализируй профиль и предложи улучшения по био, аватару, pinned репозиториям",
            "activity": "Оцени активность и предложи способы увеличения вклада в сообщество",
            "overall": "Дай общие рекомендации по улучшению всего профиля"
        }
        
        focus_text = focus_prompts.get(focus_area, focus_prompts["overall"])
        prompt = f"{focus_text}\n\nДанные профиля:\n{profile_data}\n\nФокус на: {focus_area}\n\nФормат ответа: Markdown с:\n- Анализом текущего состояния в указанной области\n- 5-7 конкретными рекомендациями\n- Приоритетами улучшений\n- Примеры реализации"
        
        return self._get_openai_analysis(prompt)
    
    def _generate_goals(self, username: str, timeframe: str) -> str:
        """Генерация целей для развития"""
        logger.info(f"Генерирую цели для {username} на период {timeframe}")
        
        profile_data = self._get_profile_data(username)
        
        timeframe_descriptions = {
            "short": "1-3 месяца",
            "medium": "3-6 месяцев", 
            "long": "6-12 месяцев"
        }
        
        timeframe_text = timeframe_descriptions[timeframe]
        prompt = f"На основе анализа GitHub профиля сгенерируй SMART цели для развития на период {timeframe_text}:\n\n{profile_data}\n\nЗадача: Создай 5-7 конкретных, измеримых, достижимых, релевантных и ограниченных по времени целей.\n\nФормат ответа: Markdown с:\n- Кратким анализом текущего состояния\n- Целями по категориям (код, активность, профиль, навыки)\n- Конкретными метриками для каждой цели\n- Планом действий по достижению\n- Критериями успеха"
        
        return self._get_openai_analysis(prompt)
    
    def _compare_with_peers(self, username: str, peer_usernames: List[str]) -> str:
        """Сравнение с похожими профилями"""
        logger.info(f"Сравниваю {username} с {peer_usernames}")
        
        # Получаем данные основного профиля
        main_profile = self._get_profile_data(username)
        
        # Получаем данные peer профилей
        peer_profiles = []
        for peer in peer_usernames:
            try:
                peer_data = self._get_profile_data(peer)
                peer_profiles.append(f"=== {peer} ===\n{peer_data}")
            except Exception as e:
                logger.warning(f"Не удалось получить данные для {peer}: {e}")
                peer_profiles.append(f"=== {peer} ===\nДанные недоступны")
        
        peer_text = '\n\n'.join(peer_profiles)
        prompt = f"Сравни следующий GitHub профиль с peer профилями и дай рекомендации:\n\nОсновной профиль ({username}):\n{main_profile}\n\nPeer профили:\n{peer_text}\n\nЗадача: Проанализируй различия и предложи:\n1. Что можно улучшить в основном профиле\n2. Какие лучшие практики перенять от peers\n3. Конкретные шаги для развития\n4. Области для фокуса\n\nФормат ответа: Markdown с анализом и рекомендациями"
        
        return self._get_openai_analysis(prompt)
    
    def _get_profile_data(self, username: str) -> str:
        """Получает данные профиля (симулирует вызов первого MCP)"""
        try:
            # Получаем профиль
            profile = self.github_client.get_user_profile_by_username(username)
            
            # Получаем репозитории
            repos = self.github_client.get_user_repositories_by_username(username, per_page=100)
            
            # Статистика уже есть в profile
            # stats = self.github_client.get_user_statistics(username)
            
            # Формируем структурированные данные
            profile_data = f"## Профиль пользователя: {username}\n\n### Основная информация:\n- Имя: {profile.get('name', 'Не указано')}\n- Bio: {profile.get('bio', 'Не указано')}\n- Компания: {profile.get('company', 'Не указано')}\n- Локация: {profile.get('location', 'Не указано')}\n- Сайт: {profile.get('blog', 'Не указано')}\n- Twitter: {profile.get('twitter_username', 'Не указано')}\n\n### Статистика:\n- Публичных репозиториев: {profile.get('public_repos', 0)}\n- Публичных gists: {profile.get('public_gists', 0)}\n- Подписчиков: {profile.get('followers', 0)}\n- Подписок: {profile.get('following', 0)}\n- Дата создания: {profile.get('created_at', 'Не указано')}\n- Последняя активность: {profile.get('updated_at', 'Не указано')}\n\n### Репозитории (топ 10 по звездам):"
            
            # Добавляем топ репозитории
            sorted_repos = sorted(repos, key=lambda x: x.get('stargazers_count', 0), reverse=True)
            for repo in sorted_repos[:10]:
                repo_name = repo['name']
                repo_desc = repo.get('description', 'Без описания')
                repo_lang = repo.get('language', 'Не указан')
                repo_stars = repo.get('stargazers_count', 0)
                repo_forks = repo.get('forks_count', 0)
                repo_size = repo.get('size', 0)
                repo_updated = repo.get('updated_at', 'Не указано')
                
                profile_data += f"\n- {repo_name}: {repo_desc}\n  - Язык: {repo_lang}\n  - Звезды: {repo_stars}\n  - Форки: {repo_forks}\n  - Размер: {repo_size} KB\n  - Последнее обновление: {repo_updated}"
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Ошибка при получении данных профиля: {e}")
            return f"Ошибка при получении данных профиля: {str(e)}"
    
    def _get_openai_analysis(self, prompt: str) -> str:
        """Получает анализ от OpenAI API"""
        try:
            logger.info("Отправляю запрос в OpenAI API")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты эксперт по анализу GitHub профилей и рекомендациям по их улучшению. Отвечай на русском языке."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            analysis = response.choices[0].message.content
            logger.info("Получен ответ от OpenAI API")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Ошибка при обращении к OpenAI API: {e}")
            return f"Ошибка при анализе через AI: {str(e)}"


if __name__ == "__main__":
    # Тестирование сервера
    server = GitHubAIAdvisorMCPServer()
    
    print("Доступные тулсы:")
    for tool in server.list_tools():
        print(f"- {tool['name']}: {tool['description']}")
    
    # Тест анализа профиля
    print("\nТестирую analyze_profile...")
    try:
        result = server.call_tool("analyze_profile", {"username": "ilyapopov24"})
        print("Результат:", result)
    except Exception as e:
        print(f"Ошибка: {e}")
