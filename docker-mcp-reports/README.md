# MCP Report Generator

Автоматический генератор отчетов на основе GitHub данных с отправкой по email.

## 🚀 Возможности

- **Автоматический сбор данных** GitHub профиля и репозиториев
- **Генерация отчетов** по технологическому стеку и активности
- **Отправка по расписанию** через SMTP (Gmail, Yandex)
- **Docker контейнеризация** для простого развертывания
- **Логирование** всех операций

## 📋 Требования

- Docker
- Docker Compose
- GitHub Personal Access Token
- Email аккаунт (Gmail или Yandex)

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
# Сборка и запуск
./start.sh start

# Остановка
./start.sh stop

# Перезапуск
./start.sh restart

# Просмотр логов
./start.sh logs
```

## 📁 Структура проекта

```
docker-mcp-reports/
├── src/                    # Исходный код
│   ├── main.py            # Главный модуль
│   ├── github_client.py   # GitHub API клиент
│   ├── email_sender.py    # Отправка email
│   └── report_generator.py # Генерация отчетов
├── config/                 # Конфигурация
├── logs/                   # Логи (автоматически создается)
├── data/                   # Данные (автоматически создается)
├── Dockerfile              # Docker образ
├── docker-compose.yml      # Docker Compose
├── requirements.txt        # Python зависимости
├── start.sh               # Скрипт управления
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

## 📝 Логирование

Логи сохраняются в директории `logs/` и доступны через:

```bash
# Логи контейнера
docker logs mcp-report-generator

# Логи приложения
tail -f logs/mcp_reports.log
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
