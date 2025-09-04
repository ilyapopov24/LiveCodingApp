# 🧠 АГЕНТ КОНТЕКСТ - MCP + Docker + Cursor

## 🎯 ЧТО ЭТО ЗА ПРОЕКТ
**LiveCodingApp** - проект с двумя отдельными направлениями:

### 1. Android приложение
- **Назначение**: Приложение для анализа GitHub профилей и репозиториев
- **Функции**: 
  - Просмотр персонажей Rick and Morty (тестовые данные)
  - Чат с AI через Gemini API
  - Анализ GitHub аналитики
  - MCP чат интеграция
- **Архитектура**: MVVM, Clean Architecture, Room, Retrofit
- **Технологии**: Kotlin, Android SDK, Material 3, Navigation Component

### 2. MCP серверы  
- **Назначение**: Набор Model Context Protocol серверов через Docker для Cursor IDE
- **Функции**: GitHub аналитика, AI советник, Python runner
- **Архитектура**: Docker контейнеры, STDIO протокол, Python

**Работаем с обоими направлениями параллельно** - Android приложение и MCP серверы развиваются независимо друг от друга.

## 🏗️ АРХИТЕКТУРА
- **3 MCP сервера** работают в Docker контейнерах
- **STDIO протокол** для связи с Cursor
- **Volume mounting** для доступа к файлам хоста
- **Keepalive скрипты** для поддержания соединения

## 🚀 MCP СЕРВЕРЫ

### 1. GitHub Analytics (11 тулсов)
- **Команда**: `mcp`
- **Образ**: `docker-mcp-reports-mcp-server:latest`
- **Файл**: `src/mcp_keepalive.py`

### 2. GitHub AI Advisor (5 тулсов)  
- **Команда**: `mcp-ai`
- **Образ**: `docker-mcp-reports-mcp-ai-advisor:latest`
- **Файл**: `src/ai_advisor_keepalive.py`

### 3. Python Runner (1 тулса)
- **Команда**: `python-runner`
- **Образ**: `docker-mcp-reports-python-runner:latest`
- **Файл**: `src/python_runner_keepalive.py`
- **Тулса**: `run-python-file` (выполняет Python файлы)

## 🔧 КЛЮЧЕВЫЕ ПАТТЕРНЫ

### JSON Parsing Issue (КРИТИЧНО!)
При работе с JSON API, которые используют snake_case (used_tokens, daily_limit, user_role) и Kotlin data classes с camelCase (usedTokens, dailyLimit, userRole), ВСЕГДА добавлять @SerializedName аннотации для маппинга полей.

**Это частая ошибка, которая приводит к десериализации null значений вместо реальных данных из API.**

**Пример:**
```kotlin
data class LoginResponse(
    @SerializedName("access_token")
    val accessToken: String?,
    @SerializedName("token_type") 
    val tokenType: String?,
    @SerializedName("user_role")
    val userRole: String?
)
```

**Без аннотаций:** API возвращает `{"access_token":"abc"}`, но Gson десериализует в `LoginResponse(accessToken=null, tokenType=null, userRole=null)`

**С аннотациями:** API возвращает `{"access_token":"abc"}`, Gson правильно десериализует в `LoginResponse(accessToken="abc", tokenType=null, userRole=null)`

### Docker конфигурация
```yaml
# docker-compose.yml - ВСЕГДА включай:
restart: unless-stopped
env_file: .env
volumes:
  - ./src:/app/src
networks:
  - mcp-network
```

### MCP Keepalive паттерн
```python
# ВСЕГДА используй этот паттерн для STDIO:
while True:
    line = sys.stdin.readline()
    if not line:
        break
    # Обработка MCP сообщений
```

### Volume Mount для доступа к файлам
```yaml
# docker-compose.yml - ПРАВИЛЬНЫЙ volume mount:
volumes:
  - /Users/ilyapopov/Downloads/LiveCodingApp:/host  # Доступ к файлам хоста

# НЕПРАВИЛЬНО:
volumes:
  - /Users/ilyapopov/Downloads/LiveCodingApp/test-project:/app/test-project
```

## ❌ ЧТО НЕ РАБОТАЕТ

### Docker команды
- ❌ `docker exec` - создает новый процесс каждый раз
- ✅ `docker run --rm -i` - интерактивный режим для MCP

### MCP конфигурация  
- ❌ Пустые `capabilities.tools: {}`
- ✅ Правильные тулсы из `server.list_tools()`

### Пути к файлам
- ❌ Абсолютные пути хоста `/Users/...`
- ✅ Пути через volume mount `/host/...`

## 🚨 КРИТИЧЕСКИЕ ОШИБКИ И ИХ ИСПРАВЛЕНИЯ

### ❌ ОШИБКА: "Директория проекта не найдена: /host/test-project"
**Причина**: Неправильный volume mount в docker-compose.yml
**Что происходило**: 
- В коде Python Runner'а используется путь `/host/test-project`
- Но в docker-compose.yml монтировали в `/app/test-project`
- Результат: файлы недоступны по ожидаемому пути

**Решение**: 
```yaml
# БЫЛО (НЕПРАВИЛЬНО):
volumes:
  - /Users/ilyapopov/Downloads/LiveCodingApp/test-project:/app/test-project

# СТАЛО (ПРАВИЛЬНО):
volumes:
  - /Users/ilyapopov/Downloads/LiveCodingApp:/host
```

**Проверка**: `docker exec container-name ls -la /host/test-project`

### ❌ ОШИБКА: "No tools or prompts"
**Причина**: Пустые capabilities.tools
**Решение**: 
```python
capabilities = {"tools": {tool["name"]: tool for tool in tools}}
```

### ❌ ОШИБКА: "Container not running"
**Причина**: Неправильный режим Docker
**Решение**: Используй `docker run --rm -i` в mcp.json

### ❌ ОШИБКА: "ModuleNotFoundError"
**Причина**: Отсутствующие зависимости в requirements.txt
**Решение**: Проверь requirements.txt и пересобери образ

## 🔄 ПРОЦЕСС ИСПРАВЛЕНИЯ ПРОБЛЕМ

### 1. Анализ ошибки
- **ВСЕГДА читай логи** - они показывают точную причину
- **Проверяй volume mount** - самая частая проблема
- **Следуй AGENT_CONTEXT.md** - там написаны правильные паттерны

### 2. Исправление volume mount
```bash
# 1. Останови контейнеры
docker-compose down

# 2. Исправь docker-compose.yml
# 3. Запусти заново
docker-compose up -d

# 4. Проверь доступность файлов
docker exec container-name ls -la /host
```

### 3. Проверка исправления
```bash
# Проверь, что файлы доступны
docker exec container-name ls -la /host/test-project

# Проверь логи
docker logs container-name -f
```

## 📁 КЛЮЧЕВЫЕ ФАЙЛЫ

### Обязательные для изменения
- `docker-compose.yml` - сервисы и их конфигурация
- `entrypoint.sh` - маршрутизация команд
- `src/*_keepalive.py` - STDIO интерфейсы
- `src/*_mcp_server.py` - логика MCP серверов

### НЕ ТРОГАТЬ (пользователь сам)
- `mcp.json` - конфигурация Cursor
- `.env` - переменные окружения

## 🔄 ПРОЦЕСС РАБОТЫ

### 1. Создание нового MCP сервера
1. Создай `src/new_server_mcp_server.py` с логикой
2. Создай `src/new_server_keepalive.py` с STDIO
3. Добавь сервис в `docker-compose.yml`
4. Обнови `entrypoint.sh` с новой командой
5. Пересобери образ: `docker-compose build new-service`
6. Запусти: `docker-compose up -d new-service`

### 2. Исправление проблем
1. **ВСЕГДА читай AGENT_CONTEXT.md** - там есть решения
2. Проверь логи: `docker logs container-name -f`
3. Проверь статус: `docker ps`
4. **Проверь volume mount** - самая частая проблема
5. Пересобери при необходимости
6. Перезапусти Cursor для применения изменений

## 💡 ВАЖНЫЕ ПРИНЦИПЫ

1. **ВСЕГДА читай AGENT_CONTEXT.md** перед началом работы
2. **Всегда используй keepalive паттерн** для STDIO
3. **Volume mount для доступа к файлам хоста** - `/host/` а не `/app/`
4. **Правильные capabilities.tools** в initialize
5. **Docker run --rm -i** для интерактивности
6. **Пересборка образов** после изменения кода
7. **Перезапуск Cursor** после изменения mcp.json

## 🚨 КРИТИЧЕСКИЕ ЗАПОМНИТЬ

### Volume Mount - ГЛАВНОЕ ПРАВИЛО
```yaml
# ПРАВИЛЬНО - монтируй корневую папку в /host
volumes:
  - /Users/ilyapopov/Downloads/LiveCodingApp:/host

# НЕПРАВИЛЬНО - не монтируй подпапки в /app
volumes:
  - /Users/ilyapopov/Downloads/LiveCodingApp/test-project:/app/test-project
```

### Пути к файлам
- ❌ **НЕ используй**: `/Users/ilyapopov/Downloads/LiveCodingApp/test-project`
- ✅ **ИСПОЛЬЗУЙ**: `/host/test-project`

### Проверка работоспособности
```bash
# ВСЕГДА проверяй после изменения volume mount:
docker exec container-name ls -la /host
docker exec container-name ls -la /host/test-project
```

## 🎯 ЦЕЛЬ
Новый агент должен сразу понимать как:
- Создавать MCP серверы
- Интегрировать их с Docker
- Настраивать Cursor
- **НЕ ДОПУСКАТЬ ошибки с volume mount**
- Решать типичные проблемы
- Следовать проверенным паттернам

## 📚 ИСТОРИЯ ОШИБОК (УРОКИ)

### Ошибка 1: Неправильный volume mount
- **Дата**: 27.08.2025
- **Проблема**: Монтирование в `/app/test-project` вместо `/host`
- **Решение**: Изменение на `/host` в docker-compose.yml
- **Урок**: ВСЕГДА следуй AGENT_CONTEXT.md

### Ошибка 2: Игнорирование собственной документации
- **Дата**: 27.08.2025
- **Проблема**: Не прочитал AGENT_CONTEXT.md перед началом работы
- **Решение**: Принудительное чтение документации
- **Урок**: AGENT_CONTEXT.md = источник истины

**Этот контекст = 95% знаний для работы с проектом!** 🚀

**ВАЖНО**: Если что-то не работает - ПЕРВЫМ ДЕЛОМ читай AGENT_CONTEXT.md!
