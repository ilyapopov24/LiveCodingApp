# Changelog

Все значимые изменения в проекте документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и проект следует [Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased]

### Added
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
- **OpenAI API интеграция для AI анализа**
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
