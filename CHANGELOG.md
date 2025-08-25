# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
