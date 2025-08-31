# MCP Server для GitHub Analytics

Этот MCP (Model Context Protocol) сервер предоставляет доступ к GitHub аналитике и email функциональности прямо в Cursor.

## 🚀 Возможности

### GitHub Analytics Tools
- **`get_github_profile`** - Получить профиль GitHub пользователя
- **`get_github_repositories`** - Получить список репозиториев
- **`get_github_statistics`** - Общая статистика профиля
- **`get_tech_stack_analysis`** - Анализ технологического стека
- **`generate_github_report`** - Генерация полного отчета в Markdown

### Email Tools
- **`send_github_report`** - Отправить GitHub отчет по email
- **`test_email_connection`** - Протестировать email соединение
- **`get_email_status`** - Статус email конфигурации

### System Tools
- **`get_system_status`** - Статус приложения
- **`get_application_logs`** - Получить логи
- **`validate_configuration`** - Проверить настройки

## 🛠 Установка

### 1. Запуск MCP сервера

```bash
# Перейдите в директорию проекта
cd docker-mcp-reports

# Запустите MCP сервер
./start.sh start
```

### 2. Добавление в Cursor

#### Вариант 1: Глобальная установка
Скопируйте содержимое `mcp.json` в глобальный MCP конфигурационный файл Cursor:

**macOS/Linux:**
```bash
# Создайте директорию если её нет
mkdir -p ~/.cursor/mcp

# Скопируйте конфигурацию
cp mcp.json ~/.cursor/mcp/
```

**Windows:**
```bash
# Создайте директорию если её нет
mkdir %APPDATA%\Cursor\mcp

# Скопируйте конфигурацию
copy mcp.json %APPDATA%\Cursor\mcp\
```

#### Вариант 2: Проектная установка
Скопируйте `mcp.json` в корень вашего проекта и перезапустите Cursor.

### 3. Проверка установки

В Cursor откройте Command Palette (`Cmd/Ctrl + Shift + P`) и введите:
```
MCP: List Servers
```

Вы должны увидеть `github-analytics` в списке.

## 📖 Использование

### В чате Cursor

Теперь вы можете использовать все tools прямо в чате:

```
Получи профиль GitHub пользователя ilyapopov
```

```
Сгенерируй отчет по технологическому стеку для пользователя ilyapopov
```

```
Отправь GitHub отчет для ilyapopov на email@example.com
```

### Прямой вызов tools

```
@github-analytics get_github_profile
```

```
@github-analytics get_tech_stack_analysis
```

## 🔧 Конфигурация

### Переменные окружения

Создайте `.env` файл на основе `.env.example`:

```bash
# GitHub API
GITHUB_TOKEN=your_github_token

# Email настройки
EMAIL_PROVIDER=gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SENDER_EMAIL=your_email@gmail.com
RECIPIENT_EMAILS=recipient@example.com
```

### GitHub Token

1. Перейдите в [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Создайте новый token с правами:
   - `public_repo` - для публичных репозиториев
   - `read:user` - для профиля пользователя

### Email настройки

#### Gmail
- Включите двухфакторную аутентификацию
- Создайте App Password
- Используйте `smtp.gmail.com:587`

#### Yandex
- Включите двухфакторную аутентификацию
- Создайте App Password
- Используйте `smtp.yandex.ru:465`

## 🐛 Устранение неполадок

### MCP сервер не запускается

```bash
# Проверьте статус
./start.sh status

# Посмотрите логи
./start.sh logs mcp-server

# Перезапустите
./start.sh restart
```

### Tools не работают в Cursor

1. Проверьте что MCP сервер запущен
2. Убедитесь что конфигурация скопирована правильно
3. Перезапустите Cursor
4. Проверьте логи: `./start.sh logs mcp-server`

### Ошибки GitHub API

- Проверьте валидность GitHub токена
- Убедитесь что токен имеет необходимые права
- Проверьте лимиты API (5000 запросов в час для аутентифицированных пользователей)

### Ошибки Email

- Проверьте правильность App Password
- Убедитесь что двухфакторная аутентификация включена
- Проверьте настройки SMTP сервера

## 📊 Мониторинг

### Логи

```bash
# Логи MCP сервера
./start.sh logs mcp-server

# Логи основного сервиса
./start.sh logs mcp-report-generator

# Все логи
./start.sh logs
```

### Статус

```bash
# Статус сервисов
./start.sh status

# Использование ресурсов
docker stats
```

## 🔄 Обновление

```bash
# Остановите сервисы
./start.sh stop

# Обновите код
git pull

# Пересоберите образы
./start.sh build

# Запустите заново
./start.sh start
```

## 🧪 Тестирование

```bash
# Тестирование MCP функциональности
./start.sh test-mcp

# Тестирование основного сервиса
docker-compose run --rm mcp-report-generator test
```

## 📝 Примеры использования

### Анализ профиля разработчика

```
Проанализируй GitHub профиль пользователя ilyapopov и создай отчет по его технологическому стеку
```

### Мониторинг активности

```
Получи статистику активности для пользователя ilyapopov за последний месяц
```

### Автоматические отчеты

```
Настрой автоматическую отправку еженедельных отчетов по GitHub активности на email@example.com
```

## 🤝 Поддержка

При возникновении проблем:

1. Проверьте логи: `./start.sh logs mcp-server`
2. Убедитесь что все переменные окружения настроены
3. Проверьте что Docker и Docker Compose работают
4. Создайте Issue в репозитории с описанием проблемы

## 📄 Лицензия

MIT License
