# GitHub AI Advisor MCP Server

Второй MCP сервер для анализа GitHub профилей с использованием OpenAI API.

## Описание

GitHub AI Advisor MCP сервер дополняет основной GitHub Analytics сервер, предоставляя AI-анализ и рекомендации на основе собранных данных.

## Архитектура взаимодействия

```
Cursor IDE
    ↓
GitHub AI Advisor MCP Server
    ↓ (вызывает)
GitHub Analytics MCP Server
    ↓ (получает данные)
GitHub API
```

## Доступные тулсы

### 1. `analyze_profile`
Полный анализ GitHub профиля с AI рекомендациями.

**Параметры:**
- `username` (string) - GitHub username для анализа

**Пример использования:**
```
@github-ai-advisor analyze_profile username:ilyapopov24
```

### 2. `suggest_improvements`
Конкретные улучшения для определенной области профиля.

**Параметры:**
- `username` (string) - GitHub username для анализа
- `focus_area` (string) - Область для фокуса:
  - `repos` - репозитории и качество кода
  - `profile` - профиль и био
  - `activity` - активность и вклад в сообщество
  - `overall` - общие улучшения

**Пример использования:**
```
@github-ai-advisor suggest_improvements username:ilyapopov24 focus_area:repos
```

### 3. `generate_goals`
Генерация SMART целей для развития на основе текущего профиля.

**Параметры:**
- `username` (string) - GitHub username для анализа
- `timeframe` (string) - Временной горизонт:
  - `short` - 1-3 месяца
  - `medium` - 3-6 месяцев
  - `long` - 6-12 месяцев

**Пример использования:**
```
@github-ai-advisor generate_goals username:ilyapopov24 timeframe:medium
```

### 4. `compare_with_peers`
Сравнение профиля с похожими профилями.

**Параметры:**
- `username` (string) - GitHub username для анализа
- `peer_usernames` (array) - Список username для сравнения

**Пример использования:**
```
@github-ai-advisor compare_with_peers username:ilyapopov24 peer_usernames:["user1", "user2", "user3"]
```

## Установка и настройка

### 1. Переменные окружения

Добавьте в `.env` файл:
```bash
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# GitHub API (уже должно быть)
GITHUB_TOKEN=your_github_token_here
```

### 2. Сборка Docker образа

```bash
docker-compose build mcp-ai-advisor
```

### 3. Запуск сервера

```bash
docker-compose up mcp-ai-advisor
```

### 4. Интеграция с Cursor

Добавьте в `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "github-ai-advisor": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--name",
        "mcp-ai-advisor-cursor",
        "--env-file",
        "/path/to/your/.env",
        "docker-mcp-reports-mcp-ai-advisor",
        "mcp-ai"
      ],
      "env": {}
    }
  }
}
```

## Как это работает

1. **Пользователь вызывает тулс** в Cursor IDE
2. **AI Advisor MCP сервер** получает запрос
3. **Внутренне вызывает** GitHub Analytics MCP сервер для получения данных
4. **Формирует промпт** для OpenAI API на основе полученных данных
5. **Получает AI анализ** и возвращает структурированные рекомендации

## Примеры промптов для OpenAI

### Анализ профиля
```
Проанализируй следующий GitHub профиль и дай комплексные рекомендации по улучшению:

[Данные профиля]

Задача: Оцени текущее состояние профиля и предложи конкретные улучшения по:
1. Профилю и био
2. Репозиториям и качеству кода
3. Активности и вкладу в сообщество
4. Технологическому стеку
5. Документации и README
```

### Анализ репозиториев
```
Оцени качество кода в репозиториях и предложи улучшения по структуре, тестированию, документации

[Данные репозиториев]

Фокус на: repos

Формат ответа: Markdown с:
- Анализом текущего состояния в указанной области
- 5-7 конкретными рекомендациями
- Приоритетами улучшений
- Примеры реализации
```

## Логирование

Сервер ведет подробные логи всех операций:
- Запуск и инициализация
- Получение запросов от Cursor
- Вызовы GitHub API
- Обращения к OpenAI API
- Ошибки и исключения

Логи доступны в Docker контейнере и в volume `./logs`.

## Требования

- Python 3.11+
- OpenAI API ключ
- GitHub API токен
- Docker и Docker Compose

## Устранение неполадок

### Проблема: "OpenAI API key not found"
**Решение:** Проверьте, что `OPENAI_API_KEY` добавлен в `.env` файл и передан в Docker контейнер.

### Проблема: "GitHub token invalid"
**Решение:** Убедитесь, что `GITHUB_TOKEN` валиден и имеет необходимые права доступа.

### Проблема: "Tool execution error"
**Решение:** Проверьте логи Docker контейнера для детальной информации об ошибке.

### Проблема: Медленная работа
**Решение:** OpenAI API может занимать время. Увеличьте `max_tokens` или используйте `gpt-3.5-turbo` вместо `gpt-4`.

## Разработка

### Добавление новых тулсов

1. Добавьте новый тулс в `self.tools` в `GitHubAIAdvisorMCPServer`
2. Создайте соответствующий метод `_new_tool_name`
3. Обновите `call_tool` для обработки нового тулса
4. Добавьте тесты

### Кастомизация промптов

Промпты для OpenAI можно настроить в соответствующих методах:
- `_analyze_profile`
- `_suggest_improvements`
- `_generate_goals`
- `_compare_with_peers`

### Изменение модели OpenAI

По умолчанию используется `gpt-3.5-turbo`. Для изменения модели отредактируйте `_get_openai_analysis` метод.

## Лицензия

MIT License



