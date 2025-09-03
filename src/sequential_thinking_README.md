# Sequential Thinking MCP Server

Упрощенный MCP сервер для последовательного мышления, реализующий цепочку: **мысль → проверка → ответ**.

## Особенности

- 🧠 **Простая структура**: Три этапа мышления вместо сложной системы ветвлений
- ✅ **Встроенная проверка**: Автоматический анализ мыслей и результатов проверки
- 📝 **История мыслей**: Сохранение всего процесса мышления
- 🎯 **Четкий результат**: Структурированный финальный ответ

## Архитектура

### Этапы мышления:

1. **🧠 THOUGHT** - Формулировка мысли или анализа
2. **✅ VALIDATION** - Проверка и валидация мысли
3. **🎯 ANSWER** - Формулировка финального ответа

### Компоненты:

- `sequential_thinking_mcp_server.py` - Основная логика MCP сервера
- `sequential_thinking_stdio_server.py` - STDIO интерфейс
- `sequential_thinking_Dockerfile` - Docker конфигурация
- `sequential_thinking_pyproject.toml` - Python конфигурация

## Использование

### Инструмент `sequential-thinking`

**Параметры:**
- `thought` (string, обязательный) - Ваша текущая мысль или анализ
- `stage` (string, обязательный) - Этап: "thought", "validation", "answer"
- `problem` (string, обязательный) - Описание проблемы или задачи
- `validation_result` (string, опциональный) - Результат проверки (для stage="validation")
- `final_answer` (string, опциональный) - Финальный ответ (для stage="answer")

### Пример использования:

#### 1. Этап "thought":
```json
{
  "thought": "Для решения этой задачи нужно проанализировать требования и выбрать подходящий алгоритм",
  "stage": "thought",
  "problem": "Как оптимизировать производительность приложения?"
}
```

#### 2. Этап "validation":
```json
{
  "thought": "Алгоритм A будет быстрее, но потребует больше памяти",
  "stage": "validation", 
  "problem": "Как оптимизировать производительность приложения?",
  "validation_result": "Проверил документацию - алгоритм A действительно быстрее на 30%"
}
```

#### 3. Этап "answer":
```json
{
  "thought": "Рекомендую использовать алгоритм A с кэшированием",
  "stage": "answer",
  "problem": "Как оптимизировать производительность приложения?",
  "final_answer": "Используйте алгоритм A с LRU кэшем для достижения 30% прироста производительности"
}
```

## Установка

### Docker (рекомендуется):

```bash
# Сборка образа
docker build -t sequential-thinking-mcp -f src/sequential_thinking_Dockerfile .

# Запуск
docker run --rm -i sequential-thinking-mcp
```

### Локальная установка:

```bash
# Установка зависимостей
pip install -e src/

# Запуск
python src/sequential_thinking_stdio_server.py
```

## Конфигурация MCP

### Для Claude Desktop:

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "docker",
      "args": [
        "run",
        "--rm", 
        "--interactive",
        "sequential-thinking-mcp"
      ]
    }
  }
}
```

### Для VS Code:

```json
{
  "servers": {
    "sequential-thinking": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "--interactive", 
        "sequential-thinking-mcp"
      ]
    }
  }
}
```

## Разработка

### Запуск тестов:
```bash
pytest tests/
```

### Форматирование кода:
```bash
black src/
```

### Проверка типов:
```bash
mypy src/
```

## Отличия от официального Sequential Thinking

| Функция | Официальный | Наш сервер |
|---------|-------------|------------|
| Язык | TypeScript | Python |
| Этапы | Динамические | Фиксированные (3) |
| Ветвления | Поддерживаются | Не поддерживаются |
| Ревизии | Поддерживаются | Не поддерживаются |
| Сложность | Высокая | Низкая |
| Настройка | Сложная | Простая |

## Лицензия

MIT License - см. файл LICENSE для деталей.

## Поддержка

Для вопросов и предложений создавайте issues в репозитории проекта.



