# CHANGELOG

## [1.0.0] - 2024-12-19

### Added
- Rick and Morty API интеграция для отображения персонажей
- Пагинация для списка персонажей
- Offline кэширование с Room базой данных
- Clean Architecture с MVVM паттерном
- Dependency Injection с Hilt
- MCP (Model Context Protocol) интеграция для подключения к GitHub API через готовый MCP сервер
- **Правильная архитектура согласно схеме**: Пользователь → LLM (Gemini) → AI Client → MCP Server → GitHub API
- Новая вкладка "MCP GitHub" в bottom navigation
- Gemini AI интеграция для обработки естественного языка
- GitHub API интеграция для базовых операций

### Changed
- Обновлена архитектура приложения для поддержки MCP
- Реализован MCP протокол для GitHub операций

### Technical Details
- Используется WebSocket для MCP соединения
- JSON-RPC 2.0 протокол
- Автоматическая инициализация Gemini API
- Структурированные запросы через Gemini AI

## [1.1.0] - 2024-12-19

### Added
- **Расширенная GitHub аналитика** - полный анализ профиля и репозиториев
- **Детальный анализ репозиториев** - содержимое, языки программирования, структура файлов
- **Технологический стек** - автоматическое определение используемых технологий
- **Статистика активности** - анализ коммитов, активности по времени
- **Генерация отчетов** - комплексные отчеты по GitHub профилю
- Новая вкладка "GitHub Analytics" в bottom navigation
- Расширенный GitHub API с новыми endpoints
- Domain entities для аналитических данных
- Use cases для генерации отчетов

### New GitHub Functions
- `analyze_profile` - полный анализ GitHub профиля
- `analyze_repository` - детальный анализ конкретного репозитория
- `generate_report` - создание полного отчета по профилю
- `get_technology_stack` - анализ технологического стека
- `get_activity_stats` - статистика активности
- `get_repository_structure` - структура файлов репозитория
- `list_all_repositories` - детальная информация о всех репозиториях
- `repository_details` - полная информация о конкретном репозитории
- `search_repositories` - поиск репозиториев по ключевым словам

### Enhanced GitHub API
- `/user` - информация о профиле пользователя
- `/user/repos` - расширенная информация о репозиториях
- `/repos/{owner}/{repo}/languages` - языки программирования
- `/repos/{owner}/{repo}/contents` - содержимое репозитория
- `/repos/{owner}/{repo}/commits` - история коммитов
- `/repos/{owner}/{repo}/stats/contributors` - статистика контрибьюторов

### UI Improvements
- GitHub Analytics Dashboard с карточками статистики
- Кнопки для различных типов анализа
- Отображение технологического стека
- Графики активности и статистики
- Адаптивный дизайн для аналитических данных

### Technical Improvements
- Новые data classes для расширенных GitHub данных
- Аналитические алгоритмы для определения технологий
- Кэширование аналитических данных
- Оптимизация API запросов
- Обработка ошибок и edge cases
- **Chat Integration**: Все аналитические функции теперь доступны через MCP чат
- **Enhanced Gemini Prompts**: Обновлены промпты для поддержки новых команд

### Dependencies
- Расширенный Retrofit для GitHub API
- Новые domain entities для аналитики
- Use cases для бизнес-логики
- ViewModels для UI состояния
