"""
Gemini API Client
Клиент для работы с Google Generative AI (Gemini)
"""

import logging
import google.generativeai as genai
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class GeminiClient:
    """Клиент для работы с Gemini API"""
    
    def __init__(self, api_key: str):
        """Инициализация клиента"""
        self.api_key = api_key
        self.model = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Инициализация Gemini модели"""
        try:
            if not self.api_key or self.api_key == "YOUR_GEMINI_API_KEY_HERE":
                logger.error("Gemini API ключ не настроен")
                return
            
            # Настройка API ключа
            genai.configure(api_key=self.api_key)
            
            # Попытка инициализации основной модели
            try:
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini модель успешно инициализирована: gemini-1.5-flash")
            except Exception as e:
                logger.warning(f"Не удалось инициализировать gemini-1.5-flash: {e}")
                
                # Попытка fallback моделей
                fallback_models = ['gemini-1.5-pro', 'gemini-1.0-pro', 'gemini-pro']
                
                for model_name in fallback_models:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        logger.info(f"Gemini модель успешно инициализирована: {model_name}")
                        break
                    except Exception as fallback_e:
                        logger.warning(f"Не удалось инициализировать {model_name}: {fallback_e}")
                        continue
                
                if not self.model:
                    logger.error("Не удалось инициализировать ни одну Gemini модель")
                    
        except Exception as e:
            logger.error(f"Ошибка инициализации Gemini API: {e}")
    
    def is_initialized(self) -> bool:
        """Проверка инициализации"""
        return self.model is not None
    
    def generate_github_analysis(self, profile_data: Dict[str, Any], repositories: list) -> Optional[str]:
        """Генерация анализа GitHub профиля"""
        try:
            if not self.is_initialized():
                logger.error("Gemini API не инициализирован")
                return None
            
            # Создаем промпт для анализа
            prompt = self._create_analysis_prompt(profile_data, repositories)
            
            # Генерируем ответ
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                logger.info("Анализ GitHub профиля успешно сгенерирован")
                return response.text
            else:
                logger.error("Пустой ответ от Gemini API")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка генерации анализа: {e}")
            return None
    
    def generate_technology_stack_analysis(self, repositories: list) -> Optional[str]:
        """Анализ технологического стека"""
        try:
            if not self.is_initialized():
                logger.error("Gemini API не инициализирован")
                return None
            
            prompt = self._create_tech_stack_prompt(repositories)
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                logger.info("Анализ технологического стека успешно сгенерирован")
                return response.text
            else:
                logger.error("Пустой ответ от Gemini API")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка анализа технологического стека: {e}")
            return None
    
    def generate_activity_analysis(self, profile_data: Dict[str, Any], repositories: list) -> Optional[str]:
        """Анализ активности"""
        try:
            if not self.is_initialized():
                logger.error("Gemini API не инициализирован")
                return None
            
            prompt = self._create_activity_prompt(profile_data, repositories)
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                logger.info("Анализ активности успешно сгенерирован")
                return response.text
            else:
                logger.error("Пустой ответ от Gemini API")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка анализа активности: {e}")
            return None
    
    def _create_analysis_prompt(self, profile_data: Dict[str, Any], repositories: list) -> str:
        """Создание промпта для анализа профиля"""
        return f"""
Ты - AI ассистент для анализа GitHub профилей. Проанализируй следующий профиль и создай детальный отчет.

ДАННЫЕ ПРОФИЛЯ:
{self._format_profile_data(profile_data)}

РЕПОЗИТОРИИ ({len(repositories)}):
{self._format_repositories_data(repositories)}

Создай комплексный анализ в следующем формате:

# 📊 АНАЛИЗ GITHUB ПРОФИЛЯ

## 👤 Основная информация
- Имя: [имя пользователя]
- Дата регистрации: [дата]
- Местоположение: [местоположение]
- Компания: [компания]
- Био: [биография]

## 📈 Статистика профиля
- Репозитории: [количество]
- Подписчики: [количество]
- Подписки: [количество]
- Gists: [количество]

## ⭐ Активность
- Всего звезд: [количество]
- Всего форков: [количество]
- Последнее обновление: [дата]

## 🔧 Технологический стек
- Основные языки: [языки с процентами]
- Популярные фреймворки: [фреймворки]
- Инструменты: [инструменты]

## 📝 Рекомендации по развитию
1. [рекомендация 1]
2. [рекомендация 2]
3. [рекомендация 3]

## 🎯 Инсайты
- [инсайт 1]
- [инсайт 2]
- [инсайт 3]

Отчет должен быть информативным, структурированным и содержать практические рекомендации.
"""
    
    def _create_tech_stack_prompt(self, repositories: list) -> str:
        """Создание промпта для анализа технологического стека"""
        return f"""
Проанализируй технологический стек на основе следующих репозиториев:

{self._format_repositories_data(repositories)}

Создай детальный анализ технологического стека:

# 🔧 АНАЛИЗ ТЕХНОЛОГИЧЕСКОГО СТЕКА

## 💻 Языки программирования
[Анализ языков с процентным соотношением]

## ⚡ Фреймворки и библиотеки
[Список используемых фреймворков]

## 🗄️ Базы данных
[Используемые базы данных]

## 🛠️ Инструменты и технологии
[Инструменты разработки, CI/CD, облачные сервисы]

## 📊 Статистика использования
[Количественные показатели по технологиям]

## 🚀 Рекомендации по развитию
[Советы по расширению технологического стека]
"""
    
    def _create_activity_prompt(self, profile_data: Dict[str, Any], repositories: list) -> str:
        """Создание промпта для анализа активности"""
        return f"""
Проанализируй активность GitHub профиля:

ПРОФИЛЬ: {self._format_profile_data(profile_data)}
РЕПОЗИТОРИИ: {len(repositories)} репозиториев

Создай анализ активности:

# 📈 АНАЛИЗ АКТИВНОСТИ

## 📅 Паттерны активности
[Анализ активности по времени]

## 🏆 Самые активные репозитории
[Топ репозиториев по активности]

## 📊 Статистика коммитов
[Анализ коммитов и изменений]

## 🎯 Рекомендации по продуктивности
[Советы по увеличению активности]

## 📈 Тренды развития
[Анализ развития профиля]
"""
    
    def _format_profile_data(self, profile_data: Dict[str, Any]) -> str:
        """Форматирование данных профиля"""
        return f"""
- Логин: {profile_data.get('login', 'N/A')}
- Имя: {profile_data.get('name', 'N/A')}
- Email: {profile_data.get('email', 'N/A')}
- Био: {profile_data.get('bio', 'N/A')}
- Компания: {profile_data.get('company', 'N/A')}
- Местоположение: {profile_data.get('location', 'N/A')}
- Дата регистрации: {profile_data.get('created_at', 'N/A')}
- Обновлен: {profile_data.get('updated_at', 'N/A')}
- Публичных репозиториев: {profile_data.get('public_repos', 0)}
- Подписчиков: {profile_data.get('followers', 0)}
- Подписок: {profile_data.get('following', 0)}
"""
    
    def _format_repositories_data(self, repositories: list) -> str:
        """Форматирование данных репозиториев"""
        if not repositories:
            return "Нет репозиториев"
        
        formatted = []
        for i, repo in enumerate(repositories[:10]):  # Показываем первые 10
            formatted.append(f"""
{i+1}. {repo.get('name', 'N/A')}
   - Описание: {repo.get('description', 'N/A')}
   - Язык: {repo.get('language', 'N/A')}
   - Звезды: {repo.get('stargazers_count', 0)}
   - Форки: {repo.get('forks_count', 0)}
   - Обновлен: {repo.get('updated_at', 'N/A')}
""")
        
        if len(repositories) > 10:
            formatted.append(f"\n... и еще {len(repositories) - 10} репозиториев")
        
        return "".join(formatted)
