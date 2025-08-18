# MCP Report Generator

Автоматический генератор отчетов на основе GitHub данных с отправкой по email и интеграцией с Cursor через MCP.

## 🚀 Возможности

- **Автоматический сбор данных** GitHub профиля и репозиториев
- **Генерация отчетов** по технологическому стеку и активности
- **Отправка по расписанию** через SMTP (Gmail, Yandex)
- **Docker контейнеризация** для простого развертывания
- **MCP интеграция** с Cursor для использования tools в чате
- **Логирование** всех операций

## 🔧 MCP Интеграция

Этот проект теперь включает два MCP (Model Context Protocol) сервера для Cursor:

### 1. GitHub Analytics MCP Server
- **GitHub аналитика** - профили, репозитории, статистика
- **Email функциональность** - отправка отчетов, тестирование соединений
- **Системный мониторинг** - статус, логи, конфигурация

### 2. GitHub AI Advisor MCP Server
- **AI анализ профилей** - рекомендации по улучшению
- **Генерация целей** - SMART цели для развития
- **Сравнение с peers** - анализ различий и лучших практик
- **Конкретные улучшения** - по репозиториям, профилю, активности

📖 **Подробные инструкции**:
- [MCP_README.md](MCP_README.md) - GitHub Analytics сервер
- [AI_ADVISOR_README.md](AI_ADVISOR_README.md) - AI Advisor сервер

## 📋 Требования

- Docker
- Docker Compose
- GitHub Personal Access Token
- Email аккаунт (Gmail или Yandex)
- **OpenAI API ключ** (для AI Advisor сервера)

## 🛠 Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd docker-mcp-reports
```

### 2. Настройка переменных окружения

Скопируйте пример конфигурации:

```bash
cp .env.example .env
```

Отредактируйте `.env` файл:

```bash
# GitHub API
GITHUB_TOKEN=your_github_token

# OpenAI API (для AI Advisor)
OPENAI_API_KEY=your_openai_api_key

# Email настройки
EMAIL_PROVIDER=yandex  # или gmail
SMTP_SERVER=smtp.yandex.ru
SMTP_PORT=465
SMTP_USERNAME=your_email@yandex.ru
SMTP_PASSWORD=your_app_password
SENDER_EMAIL=your_email@yandex.ru
RECIPIENT_EMAILS=recipient@example.com

# Настройки отчетов
REPORT_FREQUENCY=daily
REPORT_TIME=22:00
```

### 3. Запуск

```bash
# Сборка и запуск всех сервисов (включая оба MCP сервера)
./start.sh start

# Запуск только GitHub Analytics MCP сервера
docker-compose up mcp-server

# Запуск только AI Advisor MCP сервера
docker-compose up mcp-ai-advisor

# Остановка
./start.sh stop

# Перезапуск
./start.sh restart

# Просмотр логов
./start.sh logs

# Статус сервисов
./start.sh status
```

## 📁 Структура проекта

```
docker-mcp-reports/
├── src/                    # Исходный код
│   ├── main.py            # Главный модуль
│   ├── mcp_server.py      # MCP сервер (основная логика)
│   ├── mcp_stdio_server.py # MCP STDIO сервер для Cursor
│   ├── mcp_keepalive.py   # MCP STDIO сервер (улучшенная версия)
│   ├── ai_advisor_mcp_server.py # AI Advisor MCP сервер
│   ├── ai_advisor_stdio_server.py # AI Advisor STDIO сервер
│   ├── github_client.py   # GitHub API клиент
│   ├── email_sender.py    # Отправка email
│   └── report_generator.py # Генерация отчетов
├── config/                 # Конфигурация
├── logs/                   # Логи (автоматически создается)
├── data/                   # Данные (автоматически создается)
├── Dockerfile              # Docker образ
├── docker-compose.yml      # Docker Compose (2 сервиса)
├── requirements.txt        # Python зависимости
├── start.sh               # Скрипт управления
├── mcp.json               # MCP конфигурация для Cursor
├── MCP_README.md          # Инструкция по MCP интеграции
└── .env                   # Переменные окружения (не коммитить!)
```

## 🔧 Конфигурация

### GitHub API

1. Создайте Personal Access Token в [GitHub Settings](https://github.com/settings/tokens)
2. Добавьте токен в `.env` файл

### Email настройки

#### Gmail
- Включите двухфакторную аутентификацию
- Создайте App Password
- Используйте `smtp.gmail.com:587`

#### Yandex
- Включите двухфакторную аутентификацию
- Создайте App Password
- Используйте `smtp.yandex.ru:465`

## 📊 Формат отчетов

Отчеты включают:

- **Профиль пользователя** - имя, описание, статистика
- **Репозитории** - список, описания, языки программирования
- **Технологический стек** - анализ используемых технологий
- **Активность** - статистика коммитов, звезд, форков

## 🚀 MCP Tools

### GitHub Analytics
- `get_github_profile` - профиль пользователя
- `get_github_repositories` - список репозиториев
- `get_github_statistics` - общая статистика
- `get_tech_stack_analysis` - анализ технологий
- `generate_github_report` - полный отчет

### Email
- `send_github_report` - отправка отчета
- `test_email_connection` - тестирование соединения
- `get_email_status` - статус конфигурации

### System
- `get_system_status` - статус приложения
- `get_application_logs` - получение логов
- `validate_configuration` - проверка настроек

## 🐛 Устранение неполадок

### Ошибки SMTP
- Проверьте правильность App Password
- Убедитесь, что двухфакторная аутентификация включена
- Проверьте настройки SMTP сервера

### Ошибки GitHub API
- Проверьте валидность GitHub токена
- Убедитесь, что токен имеет необходимые права

### Проблемы с Docker
- Проверьте, что Docker запущен
- Убедитесь, что порты не заняты

### MCP интеграция
- Проверьте что MCP сервер запущен: `./start.sh status`
- Посмотрите логи: `./start.sh logs mcp-server`
- Убедитесь что конфигурация скопирована в Cursor

## 📝 Логирование

Логи сохраняются в директории `logs/` и доступны через:

```bash
# Логи основного сервиса
./start.sh logs mcp-report-generator

# Логи MCP сервера
./start.sh logs mcp-server

# Все логи
./start.sh logs
```

## 🔄 Обновление

```bash
# Остановка
./start.sh stop

# Обновление кода
git pull

# Пересборка и запуск
./start.sh build
./start.sh start
```

## 📄 Лицензия

MIT License

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📞 Поддержка

При возникновении проблем создайте Issue в репозитории.

## 🔗 Полезные ссылки

- [MCP интеграция с Cursor](MCP_README.md)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Cursor MCP документация](https://docs.cursor.com/tools/developers)
