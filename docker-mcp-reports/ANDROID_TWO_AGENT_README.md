# Android Two-Agent MCP Server

MCP сервер для мультиагентной системы Android разработки из 2 агентов.

## 🚀 Архитектура

```
Android Project → Code Analyzer → Bug Detector → Результат
```

### Агенты:

1. **Code Analyzer Agent** - анализирует Android код
   - Сканирует структуру проекта
   - Анализирует файлы (Kotlin, Java, XML)
   - Проверяет архитектуру (MVVM, Clean Architecture)
   - Анализирует зависимости
   - Оценивает качество кода

2. **Bug Detector Agent** - находит проблемы и баги
   - Ищет Android-специфичные баги
   - Проверяет на утечки памяти
   - Находит проблемы с жизненным циклом
   - Ищет проблемы с производительностью
   - Проверяет безопасность

## 🛠 Установка

### 1. Запуск MCP сервера

```bash
# Перейдите в директорию проекта
cd docker-mcp-reports

# Запустите Android Two-Agent MCP сервер
docker-compose up android-two-agent
```

### 2. Добавление в Cursor

Скопируйте содержимое `android-two-agent-mcp.json` в глобальный MCP конфигурационный файл Cursor:

**macOS/Linux:**
```bash
# Создайте директорию если её нет
mkdir -p ~/.cursor/mcp

# Скопируйте конфигурацию
cp android-two-agent-mcp.json ~/.cursor/mcp/
```

**Windows:**
```bash
# Создайте директорию если её нет
mkdir %APPDATA%\Cursor\mcp

# Скопируйте конфигурацию
copy android-two-agent-mcp.json %APPDATA%\Cursor\mcp\
```

### 3. Проверка установки

В Cursor откройте Command Palette (`Cmd/Ctrl + Shift + P`) и введите:
```
MCP: List Servers
```

Вы должны увидеть `android-two-agent` в списке.

## 📖 Использование

### В чате Cursor

Теперь вы можете использовать все tools прямо в чате:

```
Проанализируй Android проект /host/test-project
```

```
Получи сводку по Android проекту /host/test-project
```

```
Найди критические баги в Android проекте /host/test-project
```

```
Дай рекомендации по улучшению Android проекта /host/test-project
```

### Прямой вызов tools

```
@android-two-agent analyze_android_project
```

```
@android-two-agent get_project_summary
```

```
@android-two-agent get_critical_bugs
```

```
@android-two-agent get_recommendations
```

## 🔧 Доступные Tools

### 1. `analyze_android_project`
Полный анализ Android проекта через цепочку из 2 агентов.

**Параметры:**
- `project_path` (string) - Путь к Android проекту

**Пример использования:**
```
@android-two-agent analyze_android_project project_path:/host/test-project
```

### 2. `get_project_summary`
Получает сводку по Android проекту.

**Параметры:**
- `project_path` (string) - Путь к Android проекту

**Пример использования:**
```
@android-two-agent get_project_summary project_path:/host/test-project
```

### 3. `get_critical_bugs`
Получает список критических багов в Android проекте.

**Параметры:**
- `project_path` (string) - Путь к Android проекту

**Пример использования:**
```
@android-two-agent get_critical_bugs project_path:/host/test-project
```

### 4. `get_recommendations`
Получает рекомендации по улучшению Android проекта.

**Параметры:**
- `project_path` (string) - Путь к Android проекту

**Пример использования:**
```
@android-two-agent get_recommendations project_path:/host/test-project
```

### 5. `get_agent_status`
Получает статус агентов.

**Параметры:**
- Нет

**Пример использования:**
```
@android-two-agent get_agent_status
```

## 📊 Что анализируется

### Code Analyzer Agent:

- **Структура проекта**: Activities, Fragments, ViewModels, Repositories
- **Файлы**: Kotlin, Java, XML, Gradle файлы
- **Архитектура**: MVVM, Clean Architecture, Repository Pattern
- **Зависимости**: Gradle зависимости, версии
- **Качество кода**: Code smells, сложность, читаемость

### Bug Detector Agent:

- **Android-специфичные баги**: Утечки памяти, проблемы с жизненным циклом
- **Общие проблемы кода**: NPE, неиспользуемые переменные, длинные методы
- **Производительность**: findViewById в циклах, создание объектов
- **Безопасность**: Хардкод паролей, небезопасное хранение данных

## 🎯 Результат

**Полный анализ Android проекта** содержит:

1. **📊 Анализ проекта** - структура, файлы, архитектура
2. **🐛 Найденные баги** - критические, высокого приоритета, по категориям
3. **📈 Сводка** - общая оценка, состояние проекта
4. **💡 Рекомендации** - конкретные действия по улучшению

## 🚨 Требования

### Системные требования
- **Docker** 20.10+
- **Docker Compose** 2.0+
- **4GB RAM** минимум
- **20GB** свободного места

### Android проект
- **Kotlin/Java** код
- **Gradle** сборка
- **Стандартная структура** Android проекта

## 🐛 Устранение неполадок

### MCP сервер не запускается

```bash
# Проверьте статус
docker-compose ps android-two-agent

# Посмотрите логи
docker-compose logs android-two-agent

# Перезапустите
docker-compose restart android-two-agent
```

### Tools не работают в Cursor

1. Проверьте что MCP сервер запущен
2. Убедитесь что конфигурация скопирована правильно
3. Перезапустите Cursor
4. Проверьте логи: `docker-compose logs android-two-agent`

### Ошибки анализа проекта

- Проверьте что путь к проекту правильный
- Убедитесь что проект имеет стандартную Android структуру
- Проверьте права доступа к файлам проекта

## 📝 Примеры использования

### Анализ нового проекта

```
Проанализируй мой Android проект /host/my-android-app и дай рекомендации по улучшению
```

### Поиск критических проблем

```
Найди все критические баги в Android проекте /host/my-android-app
```

### Проверка архитектуры

```
Проверь архитектуру Android проекта /host/my-android-app и предложи улучшения
```

## 🔄 Обновление

```bash
# Остановите сервис
docker-compose stop android-two-agent

# Обновите код
git pull

# Пересоберите образ
docker-compose build android-two-agent

# Запустите заново
docker-compose up android-two-agent
```

## 📄 Лицензия

MIT License

---

**Android Two-Agent MCP Server** - ваш помощник в анализе и улучшении Android проектов! 🚀
