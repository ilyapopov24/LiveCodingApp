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

### Changed
- Упрощен report_generator.py (убраны Gemini зависимости)
- Обновлен Dockerfile с поддержкой MCP режима
- Переработан docker-compose.yml для MCP функциональности
- Обновлен start.sh с новыми командами

### Removed
- Gemini AI зависимости и функциональность
- Сложные AI-анализы отчетов

## [1.0.0] - 2024-01-XX

### Added
- Базовая функциональность GitHub аналитики
- Email отправка отчетов
- Docker контейнеризация
- Автоматическая генерация отчетов
- Логирование операций

### Changed
- Исходная версия проекта
