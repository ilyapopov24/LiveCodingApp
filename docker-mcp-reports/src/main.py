#!/usr/bin/env python3
"""
MCP Report Generator - Main Script
Автоматическая генерация отчетов GitHub профиля с использованием Gemini AI
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gemini_client import GeminiClient
from github_client import GitHubClient
from report_generator import ReportGenerator
from email_sender import EmailSender
from config.config import Config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_reports.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class MCPReportGenerator:
    """Основной класс для генерации отчетов MCP"""
    
    def __init__(self):
        """Инициализация компонентов"""
        self.config = Config()
        self.gemini_client = GeminiClient(self.config.gemini_api_key)
        self.github_client = GitHubClient(self.config.github_token)
        self.report_generator = ReportGenerator(self.gemini_client, self.github_client)
        self.email_sender = EmailSender(self.config)
        
    def generate_daily_report(self) -> Optional[str]:
        """Генерация ежедневного отчета"""
        try:
            logger.info("Начинаю генерацию ежедневного отчета...")
            
            # Получаем данные GitHub профиля
            profile_data = self.github_client.get_user_profile()
            if not profile_data:
                logger.error("Не удалось получить данные GitHub профиля")
                return None
                
            # Получаем username из профиля
            username = profile_data.get('login')
            if not username:
                logger.error("Не удалось получить username из профиля")
                return None
                
            # Генерируем отчет на основе GitHub данных (без AI-анализа)
            report = self.report_generator.generate_comprehensive_report(
                username
            )
            
            if report:
                logger.info("Отчет успешно сгенерирован")
                return report
            else:
                logger.error("Не удалось сгенерировать отчет")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при генерации отчета: {str(e)}")
            return None
    
    def send_report(self, report: str) -> bool:
        """Отправка отчета по email"""
        try:
            logger.info("Отправляю отчет по email...")
            
            subject = f"GitHub Analytics Report - {datetime.now().strftime('%Y-%m-%d')}"
            
            success = self.email_sender.send_email(
                subject=subject,
                body=report,
                is_html=False
            )
            
            if success:
                logger.info("Отчет успешно отправлен по email")
                return True
            else:
                logger.error("Не удалось отправить отчет по email")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при отправке email: {str(e)}")
            return False
    
    def run(self) -> bool:
        """Основной метод запуска"""
        try:
            logger.info("Запуск MCP Report Generator...")
            
            # Проверяем конфигурацию
            if not self.config.is_valid():
                logger.error("Неверная конфигурация. Проверьте настройки.")
                return False
            
            # Генерируем отчет
            report = self.generate_daily_report()
            if not report:
                logger.error("Не удалось сгенерировать отчет")
                return False
            
            # Отправляем отчет
            if self.send_report(report):
                logger.info("MCP Report Generator завершил работу успешно")
                return True
            else:
                logger.error("Не удалось отправить отчет")
                return False
                
        except Exception as e:
            logger.error(f"Критическая ошибка: {str(e)}")
            return False

def main():
    """Точка входа в программу"""
    try:
        generator = MCPReportGenerator()
        success = generator.run()
        
        if success:
            logger.info("Программа завершилась успешно")
            sys.exit(0)
        else:
            logger.error("Программа завершилась с ошибкой")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Программа прервана пользователем")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
