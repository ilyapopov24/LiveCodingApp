"""
Report Generator
Генератор отчетов на основе данных GitHub (без AI-анализа)
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from github_client import GitHubClient

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, github_client: GitHubClient):
        self.github_client = github_client

    def generate_comprehensive_report(self, username: str) -> Optional[str]:
        """Генерация комплексного отчета без AI-анализа"""
        try:
            logger.info(f"Генерирую комплексный отчет для пользователя: {username}")
            
            # Получаем базовые данные
            profile = self.github_client.get_user_profile()
            if not profile:
                logger.error("Не удалось получить профиль пользователя")
                return None

            repositories = self.github_client.get_user_repositories(username, 1000)
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
            logger.info(f"Генерирую отчет по технологическому стеку для пользователя: {username}")
            
            profile = self.github_client.get_user_profile()
            repositories = self.github_client.get_user_repositories(username, 1000)
            
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
            logger.info(f"Генерирую отчет по активности для пользователя: {username}")
            
            profile = self.github_client.get_user_profile()
            repositories = self.github_client.get_user_repositories(username, 1000)
            
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
        total_stars = sum(repo.get("stargazers_count", 0) for repo in repositories)
        total_forks = sum(repo.get("forks_count", 0) for repo in repositories)
        total_size = sum(repo.get("size", 0) for repo in repositories)
        
        # Анализируем языки программирования
        languages = {}
        for repo in repositories:
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        
        # Сортируем языки по популярности
        sorted_languages = dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))
        
        enriched_profile.update({
            "total_repositories": len(repositories),
            "total_stars": total_stars,
            "total_forks": total_forks,
            "total_size_kb": total_size,
            "languages_count": len(languages),
            "top_languages": sorted_languages,
            "repositories": repositories
        })
        
        return enriched_profile

    def _create_report_from_data(self, data: Dict[str, Any]) -> str:
        """Создание отчета на основе обогащенных данных"""
        logger.info("Создаю отчет на основе данных...")
        
        profile = data
        repositories = data.get("repositories", [])
        
        # Создаем Markdown отчет
        report = f"""# GitHub Analytics Report

## Профиль пользователя
- **Username**: {profile.get('login', 'N/A')}
- **Имя**: {profile.get('name', 'N/A')}
- **Биография**: {profile.get('bio', 'N/A')}
- **Компания**: {profile.get('company', 'N/A')}
- **Локация**: {profile.get('location', 'N/A')}
- **Дата создания**: {profile.get('created_at', 'N/A')}
- **Последнее обновление**: {profile.get('updated_at', 'N/A')}

## Общая статистика
- **Публичных репозиториев**: {profile.get('public_repos', 0)}
- **Подписчиков**: {profile.get('followers', 0)}
- **Подписок**: {profile.get('following', 0)}
- **Общее количество звезд**: {profile.get('total_stars', 0)}
- **Общее количество форков**: {profile.get('total_forks', 0)}
- **Общий размер репозиториев**: {profile.get('total_size_kb', 0)} KB

## Технологический стек
- **Количество языков**: {profile.get('languages_count', 0)}
- **Топ языки программирования**:
{self._format_languages_list(profile.get('top_languages', {}))}

## Репозитории
{self._format_repositories_list(repositories[:20])}  # Показываем первые 20

## Анализ активности
{self._generate_activity_analysis(repositories)}

---
*Отчет сгенерирован автоматически {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report

    def _format_languages_list(self, languages: Dict[str, int]) -> str:
        """Форматирование списка языков программирования"""
        if not languages:
            return "  - Нет данных"
        
        result = ""
        for lang, count in list(languages.items())[:10]:  # Топ 10
            result += f"  - {lang}: {count} репозиториев\n"
        
        return result

    def _format_repositories_list(self, repositories: List[Dict[str, Any]]) -> str:
        """Форматирование списка репозиториев"""
        if not repositories:
            return "Нет репозиториев"
        
        result = ""
        for repo in repositories:
            result += f"### {repo.get('name', 'N/A')}\n"
            result += f"- **Описание**: {repo.get('description', 'N/A')}\n"
            result += f"- **Язык**: {repo.get('language', 'N/A')}\n"
            result += f"- **Звезды**: {repo.get('stargazers_count', 0)}\n"
            result += f"- **Форки**: {repo.get('forks_count', 0)}\n"
            result += f"- **Размер**: {repo.get('size', 0)} KB\n"
            result += f"- **Создан**: {repo.get('created_at', 'N/A')}\n"
            result += f"- **Обновлен**: {repo.get('updated_at', 'N/A')}\n"
            result += f"- **URL**: {repo.get('html_url', 'N/A')}\n\n"
        
        return result

    def _generate_activity_analysis(self, repositories: List[Dict[str, Any]]) -> str:
        """Генерация анализа активности"""
        if not repositories:
            return "Нет данных для анализа активности"
        
        # Анализируем активность по датам
        now = datetime.now()
        recent_repos = []
        old_repos = []
        
        for repo in repositories:
            updated_at = repo.get('updated_at')
            if updated_at:
                try:
                    updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    days_since_update = (now - updated_date).days
                    
                    if days_since_update <= 30:
                        recent_repos.append(repo)
                    elif days_since_update > 365:
                        old_repos.append(repo)
                except:
                    pass
        
        # Анализируем популярность
        popular_repos = sorted(repositories, key=lambda x: x.get('stargazers_count', 0), reverse=True)[:5]
        
        analysis = f"""### Активность за последние 30 дней
- **Обновлено репозиториев**: {len(recent_repos)}

### Популярные репозитории
"""
        
        for repo in popular_repos:
            analysis += f"- **{repo.get('name', 'N/A')}**: {repo.get('stargazers_count', 0)} звезд, {repo.get('forks_count', 0)} форков\n"
        
        if old_repos:
            analysis += f"\n### Устаревшие репозитории (>1 года)\n"
            analysis += f"- **Количество**: {len(old_repos)}\n"
        
        return analysis

    def _analyze_languages(self, repositories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализ языков программирования"""
        languages = {}
        
        for repo in repositories:
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
                languages[lang]["repositories"].append(repo.get("name"))
        
        return languages

    def _create_tech_stack_report(self, profile: Dict[str, Any], repositories: List[Dict[str, Any]], languages_data: Dict[str, Any]) -> str:
        """Создание отчета по технологическому стеку"""
        report = f"""# Technology Stack Report - {profile.get('login', 'N/A')}

## Обзор технологического стека
- **Всего языков программирования**: {len(languages_data)}
- **Всего репозиториев**: {len(repositories)}

## Детальный анализ языков
"""
        
        # Сортируем языки по количеству репозиториев
        sorted_languages = sorted(languages_data.items(), key=lambda x: x[1]["count"], reverse=True)
        
        for lang, data in sorted_languages:
            report += f"""### {lang}
- **Количество репозиториев**: {data['count']}
- **Общее количество звезд**: {data['total_stars']}
- **Общее количество форков**: {data['total_forks']}
- **Средняя популярность**: {data['total_stars'] / data['count']:.1f} звезд на репозиторий
- **Репузитории**: {', '.join(data['repositories'][:5])}{'...' if len(data['repositories']) > 5 else ''}

"""
        
        return report

    def _create_activity_report(self, profile: Dict[str, Any], repositories: List[Dict[str, Any]], activity_data: Dict[str, Any]) -> str:
        """Создание отчета по активности"""
        report = f"""# Activity Report - {profile.get('login', 'N/A')}

## Общая активность
- **Всего репозиториев**: {len(repositories)}
- **Общее количество звезд**: {sum(repo.get('stargazers_count', 0) for repo in repositories)}
- **Общее количество форков**: {sum(repo.get('forks_count', 0) for repo in repositories)}

## Анализ популярности
"""
        
        # Сортируем по популярности
        popular_repos = sorted(repositories, key=lambda x: x.get('stargazers_count', 0), reverse=True)
        
        for i, repo in enumerate(popular_repos[:10], 1):
            report += f"{i}. **{repo.get('name', 'N/A')}** - {repo.get('stargazers_count', 0)} звезд, {repo.get('forks_count', 0)} форков\n"
        
        return report
