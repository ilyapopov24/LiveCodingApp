"""
GitHub API Client
Клиент для работы с GitHub API
"""

import logging
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class GitHubClient:
    """Клиент для работы с GitHub API"""
    
    def __init__(self, token: str):
        """Инициализация клиента"""
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "MCP-Report-Generator/1.0"
        }
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Выполнение HTTP запроса к GitHub API"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                logger.error("Неверный GitHub токен")
                return None
            elif response.status_code == 403:
                logger.error("Превышен лимит запросов к GitHub API")
                return None
            elif response.status_code == 404:
                logger.error(f"Ресурс не найден: {endpoint}")
                return None
            else:
                logger.error(f"Ошибка GitHub API: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Таймаут запроса к GitHub API")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к GitHub API: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            return None
    
    def get_user_profile(self) -> Optional[Dict[str, Any]]:
        """Получение профиля пользователя"""
        try:
            logger.info("Получаю профиль пользователя...")
            
            profile = self._make_request("/user")
            
            if profile:
                logger.info(f"Профиль получен: {profile.get('login', 'N/A')}")
                return profile
            else:
                logger.error("Не удалось получить профиль пользователя")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения профиля: {e}")
            return None
    
    def get_user_repositories(self, per_page: int = 100, page: int = 1) -> Optional[List[Dict[str, Any]]]:
        """Получение списка репозиториев пользователя"""
        try:
            logger.info(f"Получаю репозитории (страница {page}, по {per_page})...")
            
            params = {
                "per_page": per_page,
                "page": page,
                "sort": "updated",
                "direction": "desc"
            }
            
            repositories = self._make_request("/user/repos", params)
            
            if repositories:
                logger.info(f"Получено {len(repositories)} репозиториев")
                return repositories
            else:
                logger.error("Не удалось получить список репозиториев")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения репозиториев: {e}")
            return None
    
    def get_all_user_repositories(self) -> Optional[List[Dict[str, Any]]]:
        """Получение всех репозиториев пользователя (с пагинацией)"""
        try:
            logger.info("Получаю все репозитории пользователя...")
            
            all_repositories = []
            page = 1
            per_page = 100
            
            while True:
                repositories = self.get_user_repositories(per_page, page)
                
                if not repositories:
                    break
                
                all_repositories.extend(repositories)
                
                # Если получили меньше репозиториев, чем запросили, значит это последняя страница
                if len(repositories) < per_page:
                    break
                
                page += 1
                
                # Проверяем лимит API (5000 запросов в час)
                if page > 50:  # 50 страниц * 100 репозиториев = 5000
                    logger.warning("Достигнут лимит API запросов")
                    break
            
            logger.info(f"Всего получено {len(all_repositories)} репозиториев")
            return all_repositories
            
        except Exception as e:
            logger.error(f"Ошибка получения всех репозиториев: {e}")
            return None
    
    def get_repository_languages(self, repo_name: str) -> Optional[Dict[str, int]]:
        """Получение языков программирования репозитория"""
        try:
            logger.info(f"Получаю языки для репозитория {repo_name}...")
            
            # Используем текущий пользователь из токена
            languages = self._make_request(f"/repos/ilyapopov24/{repo_name}/languages")
            
            if languages:
                logger.info(f"Получены языки: {list(languages.keys())}")
                return languages
            else:
                logger.error(f"Не удалось получить языки для {repo_name}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения языков: {e}")
            return None
    
    def get_repository_contents(self, owner: str, repo: str, path: str = "") -> Optional[List[Dict[str, Any]]]:
        """Получение содержимого репозитория"""
        try:
            logger.info(f"Получаю содержимое {owner}/{repo}/{path}...")
            
            params = {"path": path} if path else {}
            contents = self._make_request(f"/repos/{owner}/{repo}/contents", params)
            
            if contents:
                logger.info(f"Получено {len(contents)} элементов содержимого")
                return contents
            else:
                logger.error(f"Не удалось получить содержимое {owner}/{repo}/{path}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения содержимого: {e}")
            return None
    
    def get_repository_commits(self, owner: str, repo: str, per_page: int = 30, page: int = 1) -> Optional[List[Dict[str, Any]]]:
        """Получение истории коммитов репозитория"""
        try:
            logger.info(f"Получаю коммиты для {owner}/{repo}...")
            
            params = {
                "per_page": per_page,
                "page": page
            }
            
            commits = self._make_request(f"/repos/{owner}/{repo}/commits", params)
            
            if commits:
                logger.info(f"Получено {len(commits)} коммитов")
                return commits
            else:
                logger.error(f"Не удалось получить коммиты для {owner}/{repo}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения коммитов: {e}")
            return None
    
    def get_repository_details(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Получение детальной информации о репозитории"""
        try:
            logger.info(f"Получаю детали репозитория {owner}/{repo}...")
            
            details = self._make_request(f"/repos/{owner}/{repo}")
            
            if details:
                logger.info(f"Получены детали репозитория {owner}/{repo}")
                return details
            else:
                logger.error(f"Не удалось получить детали {owner}/{repo}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения деталей репозитория: {e}")
            return None
    
    def get_repository_contributors(self, owner: str, repo: str) -> Optional[List[Dict[str, Any]]]:
        """Получение статистики контрибьюторов"""
        try:
            logger.info(f"Получаю статистику контрибьюторов для {owner}/{repo}...")
            
            contributors = self._make_request(f"/repos/{owner}/{repo}/stats/contributors")
            
            if contributors:
                logger.info(f"Получена статистика для {len(contributors)} контрибьюторов")
                return contributors
            else:
                logger.error(f"Не удалось получить статистику контрибьюторов для {owner}/{repo}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения статистики контрибьюторов: {e}")
            return None
    
    def search_repositories(self, query: str, per_page: int = 30, page: int = 1) -> Optional[Dict[str, Any]]:
        """Поиск репозиториев"""
        try:
            logger.info(f"Ищу репозитории по запросу: {query}")
            
            params = {
                "q": query,
                "per_page": per_page,
                "page": page
            }
            
            search_results = self._make_request("/search/repositories", params)
            
            if search_results:
                total_count = search_results.get("total_count", 0)
                logger.info(f"Найдено {total_count} репозиториев")
                return search_results
            else:
                logger.error("Не удалось выполнить поиск репозиториев")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка поиска репозиториев: {e}")
            return None
    
    def get_rate_limit_info(self) -> Optional[Dict[str, Any]]:
        """Получение информации о лимитах API"""
        try:
            logger.info("Получаю информацию о лимитах API...")
            
            rate_limit = self._make_request("/rate_limit")
            
            if rate_limit:
                resources = rate_limit.get("resources", {})
                core = resources.get("core", {})
                
                remaining = core.get("remaining", 0)
                limit = core.get("limit", 0)
                reset_time = core.get("reset", 0)
                
                if reset_time:
                    reset_datetime = datetime.fromtimestamp(reset_time)
                    logger.info(f"Лимит API: {remaining}/{limit} (сброс: {reset_datetime})")
                
                return rate_limit
            else:
                logger.error("Не удалось получить информацию о лимитах API")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения лимитов API: {e}")
            return None
    
    def is_token_valid(self) -> bool:
        """Проверка валидности токена"""
        try:
            profile = self.get_user_profile()
            return profile is not None
        except Exception:
            return False
