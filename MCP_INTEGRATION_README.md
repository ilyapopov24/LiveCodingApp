# MCP GitHub Integration

## Обзор

Этот проект интегрирует MCP (Model Context Protocol) для подключения к GitHub API через готовый MCP сервер. **Пользователи НЕ взаимодействуют напрямую с MCP сервером** - вместо этого используется архитектура из скрина:

```
Пользователь → LLM (Gemini) → AI Client → MCP Server → GitHub API
```

## Правильная архитектура

Согласно схеме из скрина:

1. **Пользователь** отправляет естественный язык (например: "создать репозиторий")
2. **LLM (Gemini)** обрабатывает естественный язык
3. **AI Client** (наше приложение) переводит в Function Calls (JSON schema)
4. **MCP Server** выполняет функции через GitHub API

**НЕТ прямого взаимодействия пользователя с MCP сервером!**

## Компоненты

### Data Layer
- **GeminiApi**: Обрабатывает естественный язык пользователя
- **MCPApi**: WebSocket клиент для соединения с MCP сервером
- **MCPRepositoryImpl**: Координирует работу Gemini и MCP
- **MCPMessageDto**: DTO классы для MCP сообщений

### Domain Layer
- **MCPRepository**: Интерфейс репозитория
- **MCPChatMessage**: Сущность для MCP сообщений

### Presentation Layer
- **MCPChatFragment**: UI для MCP чата
- **MCPChatViewModel**: ViewModel для управления состоянием
- **MCPChatAdapter**: Адаптер для отображения сообщений

## Поток данных

### 1. Пользователь → Gemini
- Пользователь вводит: "создать репозиторий test-project"
- Gemini анализирует и структурирует запрос

### 2. Gemini → AI Client
- Gemini возвращает JSON:
```json
{
  "operation": "create_repository",
  "parameters": {
    "name": "test-project",
    "description": "Test repository"
  },
  "description": "Создание нового репозитория test-project"
}
```

### 3. AI Client → MCP Server
- Приложение создает MCP сообщение с структурированными данными
- Отправляет через WebSocket в MCP сервер

### 4. MCP Server → GitHub API
- MCP сервер выполняет GitHub операцию
- Возвращает результат в приложение

## Использование

### 1. Открытие MCP чата
- Перейдите на вкладку "MCP GitHub" в bottom navigation
- Приложение автоматически инициализирует Gemini и подключится к MCP серверу

### 2. Отправка сообщений
- Введите запрос на естественном языке:
  - "Создать репозиторий test-project"
  - "Показать мои репозитории"
  - "Создать issue в репозитории livecodingapp"

### 3. Обработка запроса
- Gemini проанализирует ваш запрос
- Создаст структурированный JSON
- Отправит в MCP сервер
- Получит ответ от GitHub API

## Технические детали

### Gemini API
- Обрабатывает естественный язык пользователя
- Создает структурированные JSON запросы
- Использует Google AI SDK

### MCP Протокол
- Использует JSON-RPC 2.0
- WebSocket соединение для real-time коммуникации
- Стандартные MCP методы: initialize, tools/call

### Зависимости
```kotlin
// Google AI SDK для Gemini
implementation("com.google.ai.client.generativeai:generativeai:0.1.2")

// WebSocket для MCP соединения
implementation("org.java-websocket:Java-WebSocket:1.5.3")
```

### Конфигурация
- Gemini API Key: требуется настройка в `GeminiApi.kt`
- MCP Server URL: `wss://mcp-server.anthropic.com`
- Автоматическая инициализация Gemini и MCP при открытии фрагмента

## Важные моменты

### ⚠️ Ключевое отличие от неправильной архитектуры:
- **НЕ**: Пользователь → MCP Server
- **ДА**: Пользователь → Gemini → AI Client → MCP Server

### 🔑 Настройка Gemini API:
1. Получите API ключ от [Google AI Studio](https://aistudio.google.com/)
2. Добавьте в `gradle.properties`:
   ```properties
   GEMINI_API_KEY=ваш_реальный_ключ_здесь
   ```
3. Перезапустите приложение
4. Gemini API автоматически инициализируется при открытии MCP чата

## Возможные проблемы

### 1. Gemini API не инициализирован
- Проверьте API ключ
- Убедитесь в интернет соединении
- Проверьте логи для деталей ошибки

### 2. Ошибка подключения к MCP серверу
- Проверьте интернет соединение
- MCP сервер может быть недоступен
- Попробуйте переподключиться

### 3. Gemini не понимает запрос
- Переформулируйте запрос более четко
- Используйте простые команды
- Проверьте логи Gemini ответов

## Логирование

- **GeminiApi**: Логирует обработку естественного языка
- **MCPApi**: Логирует WebSocket соединение и MCP сообщения
- **MCPRepositoryImpl**: Логирует координацию между Gemini и MCP

## Будущие улучшения

- Улучшение промптов для Gemini
- Поддержка более сложных GitHub операций
- Кэширование ответов Gemini
- Офлайн режим для сохраненных ответов
- Интеграция с другими LLM (Claude, GPT)
