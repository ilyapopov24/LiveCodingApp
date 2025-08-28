# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **УДАЛЕННЫЙ ДОСТУП К MCP СЕРВЕРУ PYTHON-RUNNER**
  - HTTP API обертка для MCP сервера (порт 8001)
  - Tunnel сервер для внешнего доступа (порт 8002)
  - Localtunnel интеграция для публичного URL
  - Система загрузки Python файлов с удаленных компьютеров
  - Автоматическая генерация и выполнение тестов через OpenAI GPT-3.5-turbo и Claude Haiku 3.5
  - Shared Docker volume для обмена файлами между контейнерами
  - Полная интеграция с реальной тулсой test-python-code MCP сервера

### Fixed
- **DOCKER КОНТЕЙНЕРЫ И СЕТИ**
  - Исправлены права доступа к shared volume в Dockerfile
  - Упрощен entrypoint.sh для корректной работы команд
  - Исправлена конфигурация docker-compose.yml с правильными командами
  - Настроен Docker network для межконтейнерного взаимодействия
  - Исправлены проблемы с перезапуском контейнеров
- MCP (Model Context Protocol) интеграция с Cursor
- MCP сервер с STDIO transport
- 11 MCP tools для GitHub аналитики и email функциональности
- Поддержка Docker Compose с двумя сервисами
- Обновленный скрипт управления с MCP командами
- Подробная документация по MCP интеграции
- Поддержка Claude Haiku 3.5 в Python Runner MCP сервер
- Параллельное выполнение генерации тестов с OpenAI GPT-3.5-turbo и Claude Haiku 3.5
- Сравнительный анализ результатов тестирования от обеих моделей
- Сводный отчет с определением лучшего результата между моделями
- Spaceweb VPS MCP сервер для создания и управления VPS
- 3 MCP tools для Spaceweb API: get-available-config, list-vps, create-vps
- Интеграция с Spaceweb JSON-RPC 2.0 API
- Автоматическое получение доступных тарифных планов, дистрибутивов ОС и датацентров
- Создание VPS с настраиваемыми параметрами через MCP интерфейс



## [1.1.0] - 2025-08-25

### Added
- Полная очистка и пересборка Docker контейнеров
- Стабильная работа всех MCP серверов

### Changed
- Исправлена конфигурация mcp-report-generator в docker-compose.yml
- Остановлен неиспользуемый mcp-report-generator контейнер
- **ИСПРАВЛЕНО: Python Runner MCP сервер теперь использует переменные окружения вместо жестко прописанных значений**

### Fixed
- Устранены проблемы с перезапуском контейнеров
- Стабилизирована работа MCP серверов для Cursor IDE
- **ИСПРАВЛЕНО: Добавлено использование OPENAI_TEMPERATURE, ANTHROPIC_TEMPERATURE, OPENAI_MAX_TOKENS, ANTHROPIC_MAX_TOKENS**
- **ИСПРАВЛЕНО: Добавлено логирование используемых параметров для обеих моделей**

### Changed
- Упрощен report_generator.py (убраны Gemini зависимости)
- Обновлен Dockerfile с поддержкой MCP режима
- Переработан docker-compose.yml для MCP функциональности
- Обновлен start.sh с новыми командами

### Removed
- Gemini AI зависимости и функциональность
- Сложные AI-анализы отчетов

### Fixed
- Python Runner MCP сервер: добавлены отсутствующие методы list_tools() и call_tool()
- Исправлена инициализация MCP сервера для корректной работы с Cursor
- Spaceweb MCP сервер: исправлен парсинг distributive ID из osPanel вместо selectOs
- Spaceweb API: корректное использование distributive ID для создания VPS
- Исправлена ошибка "Создание услуг на основе данного образа не поддерживается"

## [1.0.0] - 2024-01-XX

### Added
- Базовая функциональность GitHub аналитики
- Email отправка отчетов
- Docker контейнеризация
- Автоматическая генерация отчетов
- Логирование операций

### Changed
- Исходная версия проекта
