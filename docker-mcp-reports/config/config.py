"""
Configuration Module
Модуль конфигурации для MCP Report Generator
"""

import os
import logging
from typing import List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Конфигурация приложения"""
    
    # GitHub API
    github_token: str = ""
    
    # Gemini API
    gemini_api_key: str = ""
    
    # Email настройки
    email_provider: str = "gmail"  # gmail, outlook, yandex, custom
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    sender_email: str = ""
    recipient_emails: List[str] = None
    
    # Настройки отчетов
    report_frequency: str = "daily"  # daily, weekly, monthly
    report_time: str = "09:00"  # Время отправки отчета (HH:MM)
    include_tech_stack: bool = True
    include_activity_analysis: bool = True
    include_recommendations: bool = True
    
    # Логирование
    log_level: str = "INFO"
    log_file: str = "mcp_reports.log"
    
    # GitHub API настройки
    github_api_timeout: int = 30
    github_max_repositories: int = 1000
    
    # Gemini API настройки
    gemini_model: str = "gemini-1.5-flash"
    gemini_max_tokens: int = 4000
    
    def __post_init__(self):
        """Инициализация после создания объекта"""
        if self.recipient_emails is None:
            self.recipient_emails = []
        
        # Загружаем настройки из переменных окружения
        self._load_from_env()
        
        # Устанавливаем значения по умолчанию для популярных провайдеров
        self._set_default_provider_settings()
    
    def _load_from_env(self):
        """Загрузка настроек из переменных окружения"""
        # GitHub API
        self.github_token = os.getenv('GITHUB_TOKEN', self.github_token)
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', self.gemini_api_key)
        
        # Email настройки
        self.email_provider = os.getenv('EMAIL_PROVIDER', self.email_provider)
        self.smtp_server = os.getenv('SMTP_SERVER', self.smtp_server)
        self.smtp_port = int(os.getenv('SMTP_PORT', str(self.smtp_port)))
        self.smtp_username = os.getenv('SMTP_USERNAME', self.smtp_username)
        self.smtp_password = os.getenv('SMTP_PASSWORD', self.smtp_password)
        self.sender_email = os.getenv('SENDER_EMAIL', self.sender_email)
        
        # Получатели из переменной окружения (разделенные запятыми)
        recipient_env = os.getenv('RECIPIENT_EMAILS', '')
        if recipient_env:
            self.recipient_emails = [email.strip() for email in recipient_env.split(',') if email.strip()]
        
        # Настройки отчетов
        self.report_frequency = os.getenv('REPORT_FREQUENCY', self.report_frequency)
        self.report_time = os.getenv('REPORT_TIME', self.report_time)
        self.include_tech_stack = os.getenv('INCLUDE_TECH_STACK', str(self.include_tech_stack)).lower() == 'true'
        self.include_activity_analysis = os.getenv('INCLUDE_ACTIVITY_ANALYSIS', str(self.include_activity_analysis)).lower() == 'true'
        self.include_recommendations = os.getenv('INCLUDE_RECOMMENDATIONS', str(self.include_recommendations)).lower() == 'true'
        
        # Логирование
        self.log_level = os.getenv('LOG_LEVEL', self.log_level)
        self.log_file = os.getenv('LOG_FILE', self.log_file)
        
        # GitHub API
        self.github_api_timeout = int(os.getenv('GITHUB_API_TIMEOUT', str(self.github_api_timeout)))
        self.github_max_repositories = int(os.getenv('GITHUB_MAX_REPOSITORIES', str(self.github_max_repositories)))
        
        # Gemini API
        self.gemini_model = os.getenv('GEMINI_MODEL', self.gemini_model)
        self.gemini_max_tokens = int(os.getenv('GEMINI_MAX_TOKENS', str(self.gemini_max_tokens)))
    
    def _set_default_provider_settings(self):
        """Установка настроек по умолчанию для популярных провайдеров"""
        if self.email_provider == 'gmail':
            if not self.smtp_server:
                self.smtp_server = "smtp.gmail.com"
            if not self.smtp_port:
                self.smtp_port = 587
        elif self.email_provider == 'outlook' or self.email_provider == 'hotmail':
            if not self.smtp_server:
                self.smtp_server = "smtp-mail.outlook.com"
            if not self.smtp_port:
                self.smtp_port = 587
        elif self.email_provider == 'yandex':
            if not self.smtp_server:
                self.smtp_server = "smtp.yandex.ru"
            if not self.smtp_port:
                self.smtp_port = 465
    
    def is_valid(self) -> bool:
        """Проверка валидности конфигурации"""
        errors = []
        
        # Проверяем обязательные поля
        if not self.github_token:
            errors.append("GitHub токен не настроен")
        
        if not self.gemini_api_key:
            errors.append("Gemini API ключ не настроен")
        
        if not self.smtp_username:
            errors.append("SMTP пользователь не настроен")
        
        if not self.smtp_password:
            errors.append("SMTP пароль не настроен")
        
        if not self.sender_email:
            errors.append("Email отправителя не настроен")
        
        if not self.recipient_emails:
            errors.append("Email получателей не настроен")
        
        # Проверяем корректность порта
        if self.smtp_port not in [25, 465, 587]:
            errors.append("Некорректный SMTP порт. Используйте 25, 465 или 587")
        
        # Проверяем частоту отчетов
        if self.report_frequency not in ['daily', 'weekly', 'monthly']:
            errors.append("Некорректная частота отчетов. Используйте daily, weekly или monthly")
        
        # Проверяем время отчета
        try:
            hour, minute = map(int, self.report_time.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError()
        except (ValueError, AttributeError):
            errors.append("Некорректное время отчета. Используйте формат HH:MM")
        
        if errors:
            for error in errors:
                logger.error(f"Ошибка конфигурации: {error}")
            return False
        
        return True
    
    def get_report_schedule_info(self) -> str:
        """Получение информации о расписании отчетов"""
        frequency_map = {
            'daily': 'ежедневно',
            'weekly': 'еженедельно',
            'monthly': 'ежемесячно'
        }
        
        return f"""
Расписание отчетов:
• Частота: {frequency_map.get(self.report_frequency, self.report_frequency)}
• Время отправки: {self.report_time}
• Включать технологический стек: {'Да' if self.include_tech_stack else 'Нет'}
• Включать анализ активности: {'Да' if self.include_activity_analysis else 'Нет'}
• Включать рекомендации: {'Да' if self.include_recommendations else 'Нет'}
"""
    
    def get_api_info(self) -> str:
        """Получение информации об API настройках"""
        return f"""
API Настройки:
• GitHub API: {'Настроен' if self.github_token else 'Не настроен'}
• Gemini API: {'Настроен' if self.gemini_api_key else 'Не настроен'}
• GitHub таймаут: {self.github_api_timeout} сек
• Максимум репозиториев: {self.github_max_repositories}
• Gemini модель: {self.gemini_model}
• Максимум токенов: {self.gemini_max_tokens:,}
"""
    
    def get_email_info(self) -> str:
        """Получение информации о email настройках"""
        return f"""
Email Настройки:
• Провайдер: {self.email_provider}
• SMTP сервер: {self.smtp_server}
• SMTP порт: {self.smtp_port}
• Пользователь: {self.smtp_username}
• Отправитель: {self.sender_email}
• Получатели: {', '.join(self.recipient_emails)}
"""
    
    def validate_github_token(self) -> bool:
        """Проверка валидности GitHub токена"""
        return bool(self.github_token and self.github_token != "YOUR_GITHUB_TOKEN_HERE")
    
    def validate_gemini_key(self) -> bool:
        """Проверка валидности Gemini API ключа"""
        return bool(self.gemini_api_key and self.gemini_api_key != "YOUR_GEMINI_API_KEY_HERE")
    
    def get_missing_configs(self) -> List[str]:
        """Получение списка отсутствующих настроек"""
        missing = []
        
        if not self.validate_github_token():
            missing.append("GitHub Personal Access Token")
        
        if not self.validate_gemini_key():
            missing.append("Gemini API Key")
        
        if not self.smtp_username:
            missing.append("SMTP Username")
        
        if not self.smtp_password:
            missing.append("SMTP Password")
        
        if not self.sender_email:
            missing.append("Sender Email")
        
        if not self.recipient_emails:
            missing.append("Recipient Emails")
        
        return missing
    
    def to_dict(self) -> dict:
        """Преобразование конфигурации в словарь"""
        return {
            'github_token': self.github_token[:10] + '...' if len(self.github_token) > 10 else self.github_token,
            'gemini_api_key': self.gemini_api_key[:10] + '...' if len(self.gemini_api_key) > 10 else self.gemini_api_key,
            'email_provider': self.email_provider,
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'smtp_username': self.smtp_username,
            'smtp_password': '***' if self.smtp_password else '',
            'sender_email': self.sender_email,
            'recipient_emails': self.recipient_emails,
            'report_frequency': self.report_frequency,
            'report_time': self.report_time,
            'include_tech_stack': self.include_tech_stack,
            'include_activity_analysis': self.include_activity_analysis,
            'include_recommendations': self.include_recommendations,
            'log_level': self.log_level,
            'log_file': self.log_file
        }
    
    def print_config_summary(self):
        """Вывод сводки конфигурации"""
        print("=" * 60)
        print("           КОНФИГУРАЦИЯ MCP REPORT GENERATOR")
        print("=" * 60)
        
        print(self.get_api_info())
        print(self.get_email_info())
        print(self.get_report_schedule_info())
        
        missing = self.get_missing_configs()
        if missing:
            print(f"\n❌ Отсутствующие настройки: {', '.join(missing)}")
        else:
            print("\n✅ Все необходимые настройки настроены")
        
        print("=" * 60)
