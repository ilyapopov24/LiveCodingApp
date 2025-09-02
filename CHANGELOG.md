# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2025-01-27

### Added
- **Voice Input/Output**: Implemented voice recognition and text-to-speech functionality in chat
  - Added `VoiceRepository` interface and `VoiceRepositoryImpl` implementation
  - Integrated Android `SpeechRecognizer` for voice-to-text conversion
  - Integrated Android `TextToSpeech` for text-to-speech synthesis
  - Redesigned chat input layout: text field separate from buttons
  - Added "🎤 Голос" button for voice input (larger, more visible)
  - Added large green speaker button (🔊) for each bot message to play audio
  - Added `RECORD_AUDIO` permission for voice recording
  - Voice input automatically converts speech to text and sends as message
  - Voice output plays bot responses using device TTS engine

- **Chat History Persistence**: Implemented persistent storage of chat messages between app restarts
  - Added `ChatMessageEntity` for Room database storage
  - Created `ChatMessageDao` for database operations
  - Updated `AppDatabase` to version 2 with chat_messages table
  - Added `ChatMessageMapper` for data layer transformations
  - Enhanced `ChatRepositoryImpl` with save/load functionality
  - Updated `ChatViewModel` to load chat history on initialization
  - Added "очисти чат" command to clear chat history
  - Messages are now automatically saved to local database and restored on app restart

- **Build Pipeline Integration**: Added new MCP tool `build-android-pipeline` to Python Runner MCP server
- **Android Chat Command**: Added recognition of "собери пайплайн" command in Android chat
- **GitHub Actions Integration**: MCP tool can trigger Android debug build workflow via GitHub API
- **PyGithub Dependency**: Added PyGithub library for GitHub API integration

### Changed
- **Database Schema**: Updated AppDatabase from version 1 to version 2 to include chat_messages table
- **Database Migration**: Added MIGRATION_1_2 to safely upgrade existing databases
- **ChatRepository Interface**: Extended with methods for persistent storage operations
- **RoomModule**: Added ChatMessageDao and ChatMessageMapper dependencies
- **Python Runner MCP Server**: Extended with build pipeline functionality
- **ChatViewModel**: Added special command handling for build pipeline requests
- **Docker Configuration**: Updated requirements.txt with PyGithub dependency

### Technical Details
- New MCP tool: `build-android-pipeline` - triggers GitHub Actions workflow
- Command recognition: "собери пайплайн" in Android chat triggers build pipeline
- GitHub API integration: Uses PyGithub to create workflow dispatch events
- Workflow target: `android-debug-build.yml` workflow in GitHub repository

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **ANDROID DEBUG BUILD PIPELINE**
  - GitHub Actions CI/CD пайплайн для автоматической debug-сборки
  - Полный пайплайн с тестами и lint проверкой (android-debug-build.yml)
  - Быстрый пайплайн для быстрой сборки без тестов (quick-debug-build.yml)
  - Локальный bash скрипт сборки с цветным выводом (build-debug.sh)
  - Makefile для удобной сборки с командами make
  - Оптимизированные Gradle настройки для debug сборки (gradle-debug.properties)
  - Подробная документация по использованию (DEBUG_BUILD_README.md)
  - Автоматическая установка APK на подключенное устройство
  - Кэширование Gradle зависимостей и оптимизации сборки
  - Генерация отчетов (lint, test) и загрузка артефактов (APK, AAB)

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
