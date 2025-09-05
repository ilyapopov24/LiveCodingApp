# Active Context

## Current Work Focus
- Тестирование sequential-thinking инструмента
- Настройка MCP серверов

## Recent Changes
- Удалены все локальные mcp.json файлы
- Обновлена конфигурация для использования только глобальных MCP настроек

## Next Steps
- Протестировать sequential-thinking инструмент
- Настроить правильную конфигурацию MCP

## Active Decisions and Considerations
- Используем только глобальные MCP настройки из ~/.cursor/mcp.json
- НЕ изменяем глобальный mcp.json самостоятельно - только предлагаем изменения пользователю
- Sequential-thinking должен работать через Docker контейнер, а не Python скрипт
## Important Notes
- НИКОГДА не изменять глобальный mcp.json файл самостоятельно
- Можно только предлагать пользователю, что в нём изменить
- Все локальные mcp.json файлы удалены
