"""
Report Generator
Генератор отчетов на основе данных GitHub (без AI-анализа)
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from github_client import GitHubClient
from gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, gemini_client: GeminiClient, github_client: GitHubClient):
        self.gemini_client = gemini_client
        self.github_client = github_client

    def generate_comprehensive_report(self, username: str) -> Optional[str]:
        """Генерация комплексного отчета без AI-анализа"""
        try:
            logger.info("Генерирую комплексный отчет на основе GitHub данных...")
            
            # Получаем базовые данные
            profile = self.github_client.get_user_profile()
            if not profile:
                logger.error("Не удалось получить профиль пользователя")
                return None

            repositories = self.github_client.get_user_repositories()
            if not repositories:
                logger.error("Не удалось получить репозитории")
                return None

            # Обогащаем данные
            enriched_data = self._enrich_data(profile, repositories)
            
            # Создаем отчет без AI-анализа
            report = self._create_report_from_data(enriched_data)
            
            logger.info("Отчет успешно сгенерирован")
            return report

        except Exception as e:
            logger.error(f"Ошибка генерации отчета: {e}")
            return None

    def generate_technology_stack_report(self, username: str) -> Optional[str]:
        """Генерация отчета по технологическому стеку"""
        try:
            logger.info("Генерирую отчет по технологическому стеку...")
            
            profile = self.github_client.get_user_profile()
            repositories = self.github_client.get_user_repositories()
            
            if not profile or not repositories:
                return None

            # Анализируем языки программирования
            languages_data = self._analyze_languages(repositories)
            
            report = self._create_tech_stack_report(profile, repositories, languages_data)
            
            logger.info("Отчет по технологическому стеку сгенерирован")
            return report

        except Exception as e:
            logger.error(f"Ошибка генерации отчета по технологическому стеку: {e}")
            return None

    def generate_activity_report(self, username: str) -> Optional[str]:
        """Генерация отчета по активности"""
        try:
            logger.info("Генерирую отчет по активности...")
            
            profile = self.github_client.get_user_profile()
            repositories = self.github_client.get_user_repositories()
            
            if not profile or not repositories:
                return None

            # Анализируем активность
            activity_data = self._analyze_activity(repositories)
            
            report = self._create_activity_report(profile, repositories, activity_data)
            
            logger.info("Отчет по активности сгенерирован")
            return report

        except Exception as e:
            logger.error(f"Ошибка генерации отчета по активности: {e}")
            return None

    def _enrich_data(self, profile: Dict[str, Any], repositories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Обогащение данных дополнительной информацией"""
        logger.info("Обогащаю данные профиля...")
        
        enriched_profile = profile.copy()
        
        # Добавляем статистику репозиториев
        enriched_profile['total_repos'] = len(repositories)
        enriched_profile['public_repos'] = len([r for r in repositories if r.get('private') == False])
        enriched_profile['private_repos'] = len([r for r in repositories if r.get('private') == True])
        
        # Анализируем языки программирования
        languages_data = self._analyze_languages(repositories)
        enriched_profile['languages'] = languages_data
        
        # Анализируем активность
        activity_data = self._analyze_activity(repositories)
        enriched_profile['activity'] = activity_data
        
        # Анализируем топ репозитории
        top_repos = self._analyze_top_repositories(repositories)
        enriched_profile['top_repositories'] = top_repos
        
        logger.info("Данные профиля обогащены дополнительной информацией")
        return enriched_profile

    def _analyze_languages(self, repositories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализ языков программирования"""
        languages_count = {}
        total_size = 0
        
        for repo in repositories:
            repo_name = repo.get('name', '')
            languages = self.github_client.get_repository_languages(repo_name)
            
            if languages:
                for lang, size in languages.items():
                    if lang in languages_count:
                        languages_count[lang] += size
                    else:
                        languages_count[lang] = size
                    total_size += size
        
        # Сортируем по размеру
        sorted_languages = sorted(languages_count.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total_size': total_size,
            'languages': sorted_languages,
            'top_languages': sorted_languages[:5]
        }

    def _analyze_activity(self, repositories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализ активности пользователя"""
        now = datetime.now()
        month_ago = now - timedelta(days=30)
        
        recent_activity = 0
        total_stars = 0
        total_forks = 0
        total_watchers = 0
        
        for repo in repositories:
            # Считаем общую статистику
            total_stars += repo.get('stargazers_count', 0)
            total_forks += repo.get('forks_count', 0)
            total_watchers += repo.get('watchers_count', 0)
            
            # Проверяем недавнюю активность
            updated_at = repo.get('updated_at')
            if updated_at:
                try:
                    updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    if updated_date > month_ago:
                        recent_activity += 1
                except:
                    pass
        
        return {
            'recent_activity': recent_activity,
            'total_stars': total_stars,
            'total_forks': total_forks,
            'total_watchers': total_watchers,
            'activity_percentage': (recent_activity / len(repositories)) * 100 if repositories else 0
        }

    def _analyze_top_repositories(self, repositories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Анализ топ репозиториев"""
        # Сортируем по звездам
        sorted_by_stars = sorted(repositories, key=lambda x: x.get('stargazers_count', 0), reverse=True)
        
        top_repos = []
        for repo in sorted_by_stars[:5]:
            top_repos.append({
                'name': repo.get('name', ''),
                'description': repo.get('description', ''),
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'language': repo.get('language', 'Unknown'),
                'updated_at': repo.get('updated_at', ''),
                'url': repo.get('html_url', '')
            })
        
        return top_repos

    def _create_report_from_data(self, data: Dict[str, Any]) -> str:
        """Создание отчета на основе данных без AI-анализа"""
        profile = data
        
        report = f"""
# 📊 ЕЖЕДНЕВНЫЙ ОТЧЕТ GITHUB ПРОФИЛЯ
## Пользователь: {profile.get('login', 'Unknown')}
## Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}

---

## 👤 ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ

**Имя:** {profile.get('name', 'Не указано')}
**Логин:** @{profile.get('login', 'Unknown')}
**Email:** {profile.get('email', 'Не указан')}
**Компания:** {profile.get('company', 'Не указана')}
**Локация:** {profile.get('location', 'Не указана')}
**Биография:** {profile.get('bio', 'Не указана')}
**Дата регистрации:** {profile.get('created_at', 'Неизвестно')}
**Последняя активность:** {profile.get('updated_at', 'Неизвестно')}

---

## 📈 СТАТИСТИКА РЕПОЗИТОРИЕВ

**Всего репозиториев:** {profile.get('total_repos', 0)}
**Публичных:** {profile.get('public_repos', 0)}
**Приватных:** {profile.get('private_repos', 0)}
**Подписчиков:** {profile.get('followers', 0)}
**Подписок:** {profile.get('following', 0)}

---

## 🚀 ТОП РЕПОЗИТОРИИ

"""
        
        top_repos = profile.get('top_repositories', [])
        for i, repo in enumerate(top_repos, 1):
            report += f"""
**{i}. {repo.get('name', 'Unknown')}**
- Описание: {repo.get('description', 'Нет описания')}
- Язык: {repo.get('language', 'Unknown')}
- ⭐ Звезды: {repo.get('stars', 0)}
- 🍴 Форки: {repo.get('forks', 0)}
- 🔗 URL: {repo.get('url', 'N/A')}

"""
        
        # Добавляем анализ языков
        languages_data = profile.get('languages', {})
        if languages_data and 'top_languages' in languages_data:
            report += """
---

## 💻 ЯЗЫКИ ПРОГРАММИРОВАНИЯ

**Топ языков по размеру кода:**
"""
            for lang, size in languages_data.get('top_languages', []):
                percentage = (size / languages_data.get('total_size', 1)) * 100
                report += f"- **{lang}**: {size:,} байт ({percentage:.1f}%)\n"
        
        # Добавляем анализ активности
        activity_data = profile.get('activity', {})
        if activity_data:
            report += f"""
---

## 📊 АНАЛИЗ АКТИВНОСТИ

**Активных репозиториев за месяц:** {activity_data.get('recent_activity', 0)}
**Процент активности:** {activity_data.get('activity_percentage', 0):.1f}%
**Общее количество звезд:** {activity_data.get('total_stars', 0):,}
**Общее количество форков:** {activity_data.get('total_forks', 0):,}
**Общее количество наблюдателей:** {activity_data.get('total_watchers', 0):,}

---

## 📝 ЗАКЛЮЧЕНИЕ

Отчет сгенерирован автоматически на основе данных GitHub API.
Анализ профиля выполнен без использования AI для экономии ресурсов.

**Время генерации:** {datetime.now().strftime('%H:%M:%S')}
**Источник данных:** GitHub REST API v3
"""
        
        return report

    def _create_tech_stack_report(self, profile: Dict[str, Any], repositories: List[Dict[str, Any]], languages_data: Dict[str, Any]) -> str:
        """Создание отчета по технологическому стеку"""
        report = f"""
# 🛠️ ОТЧЕТ ПО ТЕХНОЛОГИЧЕСКОМУ СТЕКУ
## Пользователь: {profile.get('login', 'Unknown')}
## Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}

---

## 💻 ЯЗЫКИ ПРОГРАММИРОВАНИЯ

**Общий размер кода:** {languages_data.get('total_size', 0):,} байт

**Распределение по языкам:**
"""
        
        for lang, size in languages_data.get('languages', []):
            percentage = (size / languages_data.get('total_size', 1)) * 100
            report += f"- **{lang}**: {size:,} байт ({percentage:.1f}%)\n"
        
        report += f"""
---

## 📊 СТАТИСТИКА ПРОЕКТОВ

**Всего проектов:** {len(repositories)}
**Основные технологии:** {', '.join([lang for lang, _ in languages_data.get('top_languages', [])[:3]])}

---

## 🔍 АНАЛИЗ РЕПОЗИТОРИЕВ

"""
        
        # Группируем репозитории по языкам
        repos_by_lang = {}
        for repo in repositories:
            lang = repo.get('language', 'Unknown')
            if lang not in repos_by_lang:
                repos_by_lang[lang] = []
            repos_by_lang[lang].append(repo)
        
        for lang, repos in sorted(repos_by_lang.items(), key=lambda x: len(x[1]), reverse=True):
            report += f"""
**{lang}** ({len(repos)} проектов):
"""
            for repo in repos[:3]:  # Показываем только первые 3
                report += f"- {repo.get('name', 'Unknown')} - ⭐{repo.get('stargazers_count', 0)}\n"
        
        return report

    def _create_activity_report(self, profile: Dict[str, Any], repositories: List[Dict[str, Any]], activity_data: Dict[str, Any]) -> str:
        """Создание отчета по активности"""
        report = f"""
# 📈 ОТЧЕТ ПО АКТИВНОСТИ
## Пользователь: {profile.get('login', 'Unknown')}
## Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}

---

## 📊 ОБЩАЯ СТАТИСТИКА

**Всего репозиториев:** {len(repositories)}
**Активных за месяц:** {activity_data.get('recent_activity', 0)}
**Процент активности:** {activity_data.get('activity_percentage', 0):.1f}%

---

## ⭐ ПОПУЛЯРНОСТЬ

**Общее количество звезд:** {activity_data.get('total_stars', 0):,}
**Общее количество форков:** {activity_data.get('total_forks', 0):,}
**Общее количество наблюдателей:** {activity_data.get('total_watchers', 0):,}

---

## 🏆 ТОП ПО АКТИВНОСТИ

"""
        
        # Сортируем по времени обновления
        recent_repos = sorted(repositories, key=lambda x: x.get('updated_at', ''), reverse=True)
        
        for i, repo in enumerate(recent_repos[:5], 1):
            updated_at = repo.get('updated_at', '')
            if updated_at:
                try:
                    updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    days_ago = (datetime.now() - updated_date).days
                    time_str = f"{days_ago} дней назад" if days_ago > 0 else "Сегодня"
                except:
                    time_str = "Неизвестно"
            else:
                time_str = "Неизвестно"
            
            report += f"""
**{i}. {repo.get('name', 'Unknown')}**
- Обновлен: {time_str}
- ⭐ Звезды: {repo.get('stargazers_count', 0)}
- 🍴 Форки: {repo.get('forks_count', 0)}
- Язык: {repo.get('language', 'Unknown')}

"""
        
        return report
