import json
import logging
import os
import subprocess
import glob
import tiktoken
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
            },
            "analyze_kotlin_code": {
                "name": "analyze_kotlin_code",
                "description": "Анализ Kotlin файлов в папке presentation и рекомендации по рефакторингу",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "focus_area": {
                            "type": "string",
                            "enum": ["architecture", "performance", "code_quality", "best_practices", "all"],
                            "description": "Область фокуса анализа"
                        }
                    },
                    "required": ["focus_area"]
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
            },
            {
                "name": "analyze_kotlin_code",
                "description": "Анализ Kotlin файлов в папке presentation и рекомендации по рефакторингу",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "focus_area": {
                            "type": "string",
                            "enum": ["architecture", "performance", "code_quality", "best_practices", "all"],
                            "description": "Область фокуса анализа"
                        }
                    },
                    "required": ["focus_area"]
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
            elif tool_name == "analyze_kotlin_code":
                result = self._analyze_kotlin_code(arguments["focus_area"])
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
    
    def _analyze_kotlin_code(self, focus_area: str) -> str:
        """Анализ Kotlin файлов в папке presentation"""
        logger.info(f"Начинаю анализ Kotlin кода с фокусом на: {focus_area}")
        
        try:
            # Путь к папке presentation в контейнере
            presentation_path = "/host/presentation/src/main/java/android/mentor/presentation/ui"
            
            # Проверяем существование папки
            if not os.path.exists(presentation_path):
                return f"❌ Папка {presentation_path} не найдена. Убедитесь, что volume mount настроен правильно."
            
            # Получаем все .kt файлы
            kt_files = glob.glob(os.path.join(presentation_path, "*.kt"))
            
            if not kt_files:
                return f"❌ В папке {presentation_path} не найдено .kt файлов."
            
            logger.info(f"Найдено {len(kt_files)} Kotlin файлов для анализа")
            
            # Читаем содержимое всех файлов
            files_content = {}
            for file_path in kt_files:
                file_name = os.path.basename(file_path)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        files_content[file_name] = f.read()
                    logger.info(f"✅ Прочитан файл: {file_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Не удалось прочитать {file_name}: {e}")
                    files_content[file_name] = f"Ошибка чтения файла: {str(e)}"
            
            # Формируем данные для анализа
            code_analysis = self._prepare_code_analysis(files_content, focus_area)
            
            # Создаем промпт для OpenAI
            prompt = self._create_kotlin_analysis_prompt(code_analysis, focus_area)
            
            # Получаем анализ от OpenAI
            return self._get_openai_analysis(prompt)
            
        except Exception as e:
            logger.error(f"Ошибка при анализе Kotlin кода: {e}")
            return f"❌ Ошибка при анализе Kotlin кода: {str(e)}"
    
    def _prepare_code_analysis(self, files_content: Dict[str, str], focus_area: str) -> str:
        """Подготавливает данные кода для анализа с умной фильтрацией по лимиту токенов"""
        analysis = f"# Анализ Kotlin кода в папке presentation/ui\n\n"
        analysis += f"**Фокус анализа:** {focus_area}\n\n"
        analysis += f"**Всего файлов:** {len(files_content)}\n\n"
        
        # Сортируем файлы по размеру (самые большие первыми)
        sorted_files = sorted(files_content.items(), key=lambda x: len(x[1]), reverse=True)
        
        # Пробуем добавить файлы по одному, пока не превысим лимит
        selected_files = []
        current_analysis = analysis
        
        for file_name, content in sorted_files:
            # Создаем анализ для этого файла
            file_analysis = self._create_file_analysis(file_name, content)
            test_analysis = current_analysis + file_analysis
            
            # Проверяем, поместится ли в модель
            if self.can_fit_in_model(test_analysis):
                current_analysis = test_analysis
                selected_files.append(file_name)
                logger.info(f"✅ Добавлен файл {file_name}")
            else:
                logger.info(f"⚠️ Файл {file_name} не помещается, останавливаемся")
                break
        
        # Добавляем информацию о том, сколько файлов анализируем
        if len(selected_files) < len(files_content):
            analysis += f"**Анализируем {len(selected_files)} из {len(files_content)} файлов (по лимиту токенов):**\n"
            analysis += f"**Выбранные файлы:** {', '.join(selected_files)}\n\n"
        else:
            analysis += f"**Анализируем все {len(files_content)} файлов:**\n\n"
        
        return current_analysis
    
    def _create_file_analysis(self, file_name: str, content: str) -> str:
        """Создает анализ для одного файла"""
        analysis = f"## 📄 {file_name}\n\n"
        
        # Базовый анализ файла
        lines = content.split('\n')
        total_lines = len(lines)
        non_empty_lines = len([line for line in lines if line.strip()])
        
        # Находим классы и функции
        classes = [line.strip() for line in lines if 'class ' in line and not line.strip().startswith('//')]
        functions = [line.strip() for line in lines if ('fun ' in line or 'override fun ' in line) and not line.strip().startswith('//')]
        
        analysis += f"**Размер:** {total_lines} строк ({non_empty_lines} непустых)\n"
        analysis += f"**Классы:** {len(classes)}\n"
        analysis += f"**Функции:** {len(functions)}\n\n"
        
        # Показываем структуру класса
        if classes:
            analysis += "**Классы:**\n"
            for class_line in classes:
                analysis += f"- {class_line}\n"
            analysis += "\n"
        
        # Показываем функции
        if functions:
            analysis += "**Функции:**\n"
            for func_line in functions:
                analysis += f"- {func_line}\n"
            analysis += "\n"
        
        # Показываем ПОЛНЫЙ код файла
        analysis += "**Полный код файла:**\n```kotlin\n"
        for i, line in enumerate(lines):
            analysis += f"{i+1:3d}| {line}\n"
        analysis += "```\n\n"
        
        return analysis
    
    def _create_kotlin_analysis_prompt(self, code_analysis: str, focus_area: str) -> str:
        """Создает промпт для анализа Kotlin кода"""
        
        prompt = f"""Ты эксперт по Android разработке на Kotlin. Проанализируй ПОЛНЫЙ код ниже и найди РЕАЛЬНЫЕ проблемы.

**КРИТИЧЕСКИ ВАЖНО:** 
- У тебя есть ПОЛНЫЙ код всех файлов
- Анализируй ВСЕ файлы и ВСЕ функции
- Ищи РЕАЛЬНЫЕ проблемы: неиспользуемые переменные, неправильные lifecycle методы, проблемы с архитектурой
- Указывай ТОЧНЫЕ номера строк и файлы
- Показывай КОНКРЕТНЫЕ исправления

**Код для анализа:**
{code_analysis}

**Задача:** Найди ВСЕ проблемы в этом коде. Не останавливайся на одной проблеме!

**Что искать:**
1. **Неиспользуемые методы/переменные** - проверь, действительно ли они не используются
2. **Неправильные lifecycle методы** - onCreate, onResume, onPause и т.д.
3. **Проблемы с архитектурой** - ViewModel, LiveData, Repository
4. **Проблемы с производительностью** - memory leaks, UI blocking
5. **Проблемы с кодом** - naming, functions, error handling
6. **Android best practices** - ViewBinding, Material Design, Navigation

**Формат ответа:**
1. **Проблемы по файлам** (минимум 5-10 проблем):
   - `Файл: MainActivity.kt, Строка 25: private fun checkAuth()`
   - `Проблема: Метод checkAuth() вызывается в onCreate() на строке 18, но помечен как неиспользуемый`
   - `Исправление: Убрать private, сделать fun checkAuth()`

2. **Конкретные примеры рефакторинга** с кодом до/после

3. **Приоритетные исправления** - что исправить в первую очередь

**НЕ ПИШИ:**
- Общие советы
- Абстрактные рекомендации
- Проблемы, которых нет в коде

**ПИШИ:**
- ТОЛЬКО реальные проблемы из вашего кода
- Точные номера строк
- Конкретные исправления
"""
        
        return prompt
    
    
    def count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Подсчитывает количество токенов в тексте"""
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except Exception as e:
            logger.warning(f"⚠️ Ошибка подсчета токенов: {e}, использую приблизительный подсчет")
            # Fallback: приблизительный подсчет (1 токен ≈ 4 символа)
            return len(text) // 4
    
    def can_fit_in_model(self, text: str, model: str = "gpt-3.5-turbo", completion_tokens: int = 2000) -> bool:
        """Проверяет, поместится ли текст в модель с учетом места для ответа"""
        current_tokens = self.count_tokens(text, model)
        
        # Фиксированный лимит: 10,000 токенов для входа
        max_input_tokens = 10000
        used_percentage = current_tokens / max_input_tokens * 100
        
        logger.info(f"Токены: {current_tokens}/{max_input_tokens} (использовано {used_percentage:.1f}%)")
        return current_tokens < max_input_tokens


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
    
    # Тест анализа Kotlin кода
    print("\nТестирую analyze_kotlin_code...")
    try:
        result = server.call_tool("analyze_kotlin_code", {"focus_area": "architecture"})
        print("Результат:", result)
    except Exception as e:
        print(f"Ошибка: {e}")
