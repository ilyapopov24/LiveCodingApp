"""
Email Sender
Модуль для отправки email отчетов
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from config.config import Config

logger = logging.getLogger(__name__)

class EmailSender:
    """Отправитель email отчетов"""
    
    def __init__(self, config: Config):
        """Инициализация отправителя"""
        self.config = config
        self.smtp_server = config.smtp_server
        self.smtp_port = config.smtp_port
        self.smtp_username = config.smtp_username
        self.smtp_password = config.smtp_password
        self.sender_email = config.sender_email
        self.recipient_emails = config.recipient_emails
    
    def send_email(self, subject: str, body: str, is_html: bool = False) -> bool:
        """Отправка email"""
        try:
            if not self._validate_config():
                logger.error("Неверная конфигурация email")
                return False
            
            # Создаем сообщение
            message = self._create_message(subject, body, is_html)
            
            # Отправляем сообщение
            success = self._send_message(message)
            
            if success:
                logger.info(f"Email успешно отправлен на {', '.join(self.recipient_emails)}")
                return True
            else:
                logger.error("Не удалось отправить email")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка отправки email: {e}")
            return False
    
    def send_test_email(self) -> bool:
        """Отправка тестового email"""
        try:
            subject = "MCP Report Generator - Тестовое сообщение"
            body = """
Это тестовое сообщение от системы MCP Report Generator.

Если вы получили это сообщение, значит настройки email работают корректно.

Дата отправки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

С уважением,
MCP Report Generator
"""
            
            return self.send_email(subject, body, False)
            
        except Exception as e:
            logger.error(f"Ошибка отправки тестового email: {e}")
            return False
    
    def _create_message(self, subject: str, body: str, is_html: bool) -> MIMEMultipart:
        """Создание email сообщения"""
        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = ', '.join(self.recipient_emails)
        message['Subject'] = subject
        
        # Добавляем тело сообщения
        if is_html:
            text_part = MIMEText(body, 'html', 'utf-8')
        else:
            text_part = MIMEText(body, 'plain', 'utf-8')
        
        message.attach(text_part)
        
        return message
    
    def _send_message(self, message: MIMEMultipart) -> bool:
        """Отправка сообщения через SMTP"""
        try:
            # Подключаемся к SMTP серверу
            if self.smtp_port == 587:
                # STARTTLS
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            elif self.smtp_port == 465:
                # SSL
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                # Обычное соединение
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            # Аутентификация
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            
            # Отправляем сообщение
            server.send_message(message)
            server.quit()
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Ошибка аутентификации SMTP: {e}")
            logger.error(f"Детали: сервер={self.smtp_server}, порт={self.smtp_port}, username={self.smtp_username}")
            return False
        except smtplib.SMTPRecipientsRefused:
            logger.error("Получатели отказались от сообщения")
            return False
        except smtplib.SMTPServerDisconnected:
            logger.error("Соединение с SMTP сервером разорвано")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP ошибка: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка SMTP: {e}")
            return False
    
    def _validate_config(self) -> bool:
        """Проверка конфигурации email"""
        required_fields = [
            'smtp_server',
            'smtp_port',
            'smtp_username',
            'smtp_password',
            'sender_email',
            'recipient_emails'
        ]
        
        for field in required_fields:
            value = getattr(self, field, None)
            if not value:
                logger.error(f"Отсутствует обязательное поле: {field}")
                return False
        
        # Проверяем, что recipient_emails - это список
        if not isinstance(self.recipient_emails, list) or not self.recipient_emails:
            logger.error("recipient_emails должен быть непустым списком")
            return False
        
        # Проверяем корректность порта
        if not isinstance(self.smtp_port, int) or self.smtp_port not in [25, 465, 587]:
            logger.error("Некорректный SMTP порт. Используйте 25, 465 или 587")
            return False
        
        return True
    
    def get_smtp_info(self) -> str:
        """Получение информации о SMTP настройках"""
        return f"""
SMTP Настройки:
• Сервер: {self.smtp_server}
• Порт: {self.smtp_port}
• Пользователь: {self.smtp_username}
• Отправитель: {self.sender_email}
• Получатели: {', '.join(self.recipient_emails)}
• Тип соединения: {'SSL' if self.smtp_port == 465 else 'STARTTLS' if self.smtp_port == 587 else 'Обычное'}
"""


class GmailSender(EmailSender):
    """Отправитель для Gmail"""
    
    def __init__(self, config: Config):
        """Инициализация Gmail отправителя"""
        super().__init__(config)
        
        # Gmail использует специальные настройки
        if not self.smtp_server:
            self.smtp_server = "smtp.gmail.com"
        if not self.smtp_port:
            self.smtp_port = 587
        
        logger.info("Инициализирован Gmail отправитель")
    
    def _send_message(self, message: MIMEMultipart) -> bool:
        """Отправка через Gmail SMTP"""
        try:
            # Gmail требует STARTTLS
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            # Аутентификация
            server.login(self.smtp_username, self.smtp_password)
            
            # Отправляем сообщение
            server.send_message(message)
            server.quit()
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки через Gmail: {e}")
            return False


class OutlookSender(EmailSender):
    """Отправитель для Outlook/Hotmail"""
    
    def __init__(self, config: Config):
        """Инициализация Outlook отправителя"""
        super().__init__(config)
        
        # Outlook использует специальные настройки
        if not self.smtp_server:
            self.smtp_server = "smtp-mail.outlook.com"
        if not self.smtp_port:
            self.smtp_port = 587
        
        logger.info("Инициализирован Outlook отправитель")
    
    def _send_message(self, message: MIMEMultipart) -> bool:
        """Отправка через Outlook SMTP"""
        try:
            # Outlook использует STARTTLS
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            # Аутентификация
            server.login(self.smtp_username, self.smtp_password)
            
            # Отправляем сообщение
            server.send_message(message)
            server.quit()
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки через Outlook: {e}")
            return False


class YandexSender(EmailSender):
    """Отправитель для Yandex"""
    
    def __init__(self, config: Config):
        """Инициализация Yandex отправителя"""
        super().__init__(config)
        
        # Yandex использует специальные настройки
        if not self.smtp_server:
            self.smtp_server = "smtp.yandex.ru"
        if not self.smtp_port:
            self.smtp_port = 465
        
        logger.info("Инициализирован Yandex отправитель")
    
    def _send_message(self, message: MIMEMultipart) -> bool:
        """Отправка через Yandex SMTP"""
        try:
            # Yandex использует SSL
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            
            # Для Yandex используем полный email как username
            username = self.smtp_username if '@' in self.smtp_username else f"{self.smtp_username}@yandex.ru"
            
            # Аутентификация
            server.login(username, self.smtp_password)
            
            # Отправляем сообщение
            server.send_message(message)
            server.quit()
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки через Yandex: {e}")
            logger.error(f"Детали: сервер={self.smtp_server}, порт={self.smtp_port}, username={username}")
            return False


def create_email_sender(config: Config) -> EmailSender:
    """Фабрика для создания отправителя email"""
    email_provider = config.email_provider.lower()
    
    if email_provider == 'gmail':
        return GmailSender(config)
    elif email_provider == 'outlook' or email_provider == 'hotmail':
        return OutlookSender(config)
    elif email_provider == 'yandex':
        return YandexSender(config)
    else:
        # Используем базовый класс для кастомных настроек
        return EmailSender(config)
