# Changelog

Все значимые изменения в проекте документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и проект следует [Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased]

### Added
- **Настраиваемые параметры AI для тулсы fix-android-bug**:
  - `ANTHROPIC_TEMPERATURE` - настраивается через docker-settings.env (по умолчанию 0.1)
  - `ANTHROPIC_MAX_TOKENS` - настраивается через docker-settings.env (по умолчанию 8000)
  - Добавлены комментарии в docker-settings.env для объяснения настроек
  - Перезапущены контейнеры python-runner для применения изменений
- Автоматический генератор отчетов GitHub профиля
- Docker контейнеризация для простого развертывания
- Поддержка Gmail и Yandex SMTP
- Логирование всех операций
- Автоматическая отправка отчетов по расписанию
- **MCP (Model Context Protocol) интеграция для Cursor IDE**
- **Новые тулсы для GitHub аналитики:**
  - `get_github_profile` - получение профиля пользователя
  - `get_github_repositories` - получение списка репозиториев
  - `get_github_statistics` - получение общей статистики
  - `get_tech_stack_analysis` - анализ технологического стека
- **Второй MCP сервер: GitHub AI Advisor**
  - `analyze_profile` - полный анализ профиля с AI рекомендациями
  - `suggest_improvements` - конкретные улучшения для определенной области
  - `generate_goals` - генерация целей для развития
  - `compare_with_peers` - сравнение с похожими профилями
- **Третий MCP сервер: Python Runner**
  - `run-python-file` - запуск Python файлов
  - `test-python-code` - генерация и запуск тестов (OpenAI GPT-3.5-turbo + Claude Haiku 3.5)
- **Четвертый MCP сервер: Spaceweb VPS**
  - `create-vps` - создание VPS на Spaceweb через JSON-RPC API
- **OpenAI API интеграция для AI анализа**
- **Anthropic API интеграция для Claude Haiku 3.5**
- **STDIO transport для MCP серверов**

### Changed
- Упрощена архитектура без AI-анализа для стабильности
- Оптимизированы Docker настройки
- Улучшено логирование ошибок SMTP
- **Обновлен entrypoint.sh для поддержки двух MCP команд**
- **Добавлена поддержка OpenAI API**
- **Архитектура MCP серверов для взаимодействия**

### Fixed
- Исправлены проблемы с импортами Python модулей
- Решены проблемы с SMTP аутентификацией
- Исправлены ошибки в Docker конфигурации
- **Исправлен Python Runner MCP сервер**: добавлены недостающие методы `list_tools()` и `call_tool()`
- **Исправлен Spaceweb MCP сервер**: обновлены параметры API согласно официальной документации JSON-RPC 2.0
- **🚨 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ**: Исправлен volume mount в docker-compose.yml
  - **Проблема**: Неправильный mount `/app/test-project` вместо `/host`
  - **Результат**: Python Runner не мог найти файлы проекта
  - **Решение**: Изменен volume mount на `/host` для доступа к файлам хоста
  - **Дата**: 27.08.2025

## [1.0.0] - 2024-12-19

### Added
- Базовая функциональность генератора отчетов
- GitHub API интеграция
- Email отправка через SMTP
- Docker поддержка
- Автоматическое планирование задач

### Technical Details
- Python 3.11
- Docker Compose
- GitHub REST API v3
- SMTP протокол
- JSON логирование
