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
```json
// mcp.json - для python-runner:
"-v", "/Users/ilyapopov/Downloads/LiveCodingApp:/host"
// Файлы доступны по пути /host/ внутри контейнера
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

## 🚨 ТИПИЧНЫЕ ОШИБКИ И ИХ ИСПРАВЛЕНИЯ

### "No tools or prompts"
**Причина**: Пустые capabilities.tools
**Решение**: 
```python
capabilities = {"tools": {tool["name"]: tool for tool in tools}}
```

### "Container not running"
**Причина**: Неправильный режим Docker
**Решение**: Используй `docker run --rm -i` в mcp.json

### "File not found" в Python Runner
**Причина**: Неправильный путь к файлу
**Решение**: Используй `/host/` вместо абсолютного пути хоста

### "ModuleNotFoundError"
**Причина**: Отсутствующие зависимости в requirements.txt
**Решение**: Проверь requirements.txt и пересобери образ

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
1. Проверь логи: `docker logs container-name -f`
2. Проверь статус: `docker ps`
3. Пересобери при необходимости
4. Перезапусти Cursor для применения изменений

## 💡 ВАЖНЫЕ ПРИНЦИПЫ

1. **Всегда используй keepalive паттерн** для STDIO
2. **Volume mount для доступа к файлам хоста**
3. **Правильные capabilities.tools** в initialize
4. **Docker run --rm -i** для интерактивности
5. **Пересборка образов** после изменения кода
6. **Перезапуск Cursor** после изменения mcp.json

## 🎯 ЦЕЛЬ
Новый агент должен сразу понимать как:
- Создавать MCP серверы
- Интегрировать их с Docker
- Настраивать Cursor
- Решать типичные проблемы
- Следовать проверенным паттернам

**Этот контекст = 90% знаний для работы с проектом!** 🚀
