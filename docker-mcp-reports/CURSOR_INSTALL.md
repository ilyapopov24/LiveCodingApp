# Установка MCP сервера в Cursor

Пошаговая инструкция по добавлению GitHub Analytics MCP сервера в Cursor.

## 🚀 Быстрая установка

### Шаг 1: Запуск MCP сервера

```bash
# Перейдите в директорию проекта
cd docker-mcp-reports

# Запустите MCP сервер
./start.sh start
```

### Шаг 2: Копирование конфигурации в Cursor

#### macOS/Linux:
```bash
# Создайте директорию если её нет
mkdir -p ~/.cursor/mcp

# Скопируйте конфигурацию
cp mcp.json ~/.cursor/mcp/
```

#### Windows:
```bash
# Создайте директорию если её нет
mkdir %APPDATA%\Cursor\mcp

# Скопируйте конфигурацию
copy mcp.json %APPDATA%\Cursor\mcp\
```

### Шаг 3: Перезапуск Cursor

Закройте и откройте Cursor заново.

### Шаг 4: Проверка установки

В Cursor откройте Command Palette (`Cmd/Ctrl + Shift + P`) и введите:
```
MCP: List Servers
```

Вы должны увидеть `github-analytics` в списке.

## 🔧 Детальная установка

### Предварительные требования

1. **Docker** - должен быть установлен и запущен
2. **Docker Compose** - для управления сервисами
3. **GitHub Token** - для доступа к GitHub API
4. **Email настройки** - для отправки отчетов

### Настройка переменных окружения

1. Скопируйте `.env.example` в `.env`:
```bash
cp .env.example .env
```

2. Отредактируйте `.env` файл:
```bash
# GitHub API
GITHUB_TOKEN=your_github_token_here

# Email настройки
EMAIL_PROVIDER=gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SENDER_EMAIL=your_email@gmail.com
RECIPIENT_EMAILS=recipient@example.com
```

### Запуск сервисов

```bash
# Сборка и запуск
./start.sh start

# Проверка статуса
./start.sh status

# Просмотр логов
./start.sh logs mcp-server
```

### Тестирование MCP сервера

```bash
# Тестирование функциональности
./start.sh test-mcp
```

## 📖 Использование в Cursor

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

1. **Проверьте что MCP сервер запущен:**
   ```bash
   ./start.sh status
   ```

2. **Убедитесь что конфигурация скопирована правильно:**
   ```bash
   # macOS/Linux
   ls -la ~/.cursor/mcp/
   
   # Windows
   dir %APPDATA%\Cursor\mcp\
   ```

3. **Перезапустите Cursor**

4. **Проверьте логи:**
   ```bash
   ./start.sh logs mcp-server
   ```

### Ошибки GitHub API

- Проверьте валидность GitHub токена
- Убедитесь что токен имеет необходимые права
- Проверьте лимиты API (5000 запросов в час)

### Ошибки Email

- Проверьте правильность App Password
- Убедитесь что двухфакторная аутентификация включена
- Проверьте настройки SMTP сервера

## 🔍 Отладка

### Проверка логов

```bash
# Логи MCP сервера
./start.sh logs mcp-server

# Логи основного сервиса
./start.sh logs mcp-report-generator

# Все логи
./start.sh logs
```

### Проверка конфигурации

```bash
# Тестирование конфигурации
docker-compose run --rm mcp-server config
```

### Проверка Docker

```bash
# Статус контейнеров
docker ps

# Логи контейнера
docker logs mcp-github-analytics
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

## 📊 Мониторинг

### Статус сервисов

```bash
# Статус всех сервисов
./start.sh status

# Использование ресурсов
docker stats
```

### Проверка работоспособности

```bash
# Тестирование MCP функциональности
./start.sh test-mcp

# Тестирование основного сервиса
docker-compose run --rm mcp-report-generator test
```

## 🆘 Получение помощи

### Полезные команды

```bash
# Справка по скрипту
./start.sh help

# Очистка Docker ресурсов
./start.sh cleanup

# Перезапуск всех сервисов
./start.sh restart
```

### Создание Issue

При возникновении проблем:

1. Проверьте логи: `./start.sh logs mcp-server`
2. Убедитесь что все переменные окружения настроены
3. Проверьте что Docker и Docker Compose работают
4. Создайте Issue в репозитории с описанием проблемы

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

## 🎯 Готово!

После выполнения всех шагов у вас будет:

✅ **MCP сервер запущен** в Docker контейнере  
✅ **Конфигурация скопирована** в Cursor  
✅ **11 MCP tools доступны** в чате Cursor  
✅ **GitHub аналитика** работает через MCP  
✅ **Email функциональность** доступна через MCP  

Теперь вы можете использовать все функции GitHub аналитики прямо в чате Cursor!

