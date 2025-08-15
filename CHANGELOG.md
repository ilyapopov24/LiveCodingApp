# CHANGELOG

## [Unreleased]

### Added
- MCP (Model Context Protocol) интеграция для подключения к GitHub API через готовый MCP сервер
- **Правильная архитектура согласно схеме**: Пользователь → LLM (Gemini) → AI Client → MCP Server → GitHub API
- **НЕТ прямого взаимодействия пользователя с MCP сервером** - используется Gemini как посредник
- Новая вкладка "MCP GitHub" в bottom navigation
- MCPChatFragment для отображения MCP чата
- MCPChatViewModel для управления MCP состоянием
- MCPRepository для координации работы Gemini и MCP
- GeminiApi для обработки естественного языка пользователя
- MCPApi для WebSocket соединения с MCP сервером
- MCPChatAdapter для отображения MCP сообщений
- Поддержка Google AI SDK для Gemini
- WebSocket соединение для real-time MCP коммуникации

### Changed
- Обновлен AppModule для включения MCP модуля
- Расширен bottom navigation для поддержки трех вкладок
- **Исправлена архитектура**: Gemini обрабатывает естественный язык, создает структурированные запросы для MCP

### Technical Details
- Добавлены зависимости: Google AI SDK, Java-WebSocket
- Создан MCP модуль для dependency injection
- Реализован MCP протокол для GitHub операций
- Добавлена поддержка JSON-RPC 2.0 для MCP сообщений
- **Gemini API обрабатывает естественный язык и создает JSON schema для MCP**

## [Previous Versions]
- Базовое приложение с Rick and Morty персонажами
- Chat функциональность с OpenAI API
- Clean Architecture с MVVM паттерном
- Hilt dependency injection
- Room database для кэширования
