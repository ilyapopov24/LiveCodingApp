#!/bin/bash

echo "🚀 Загружаем модель Qwen:06 в Ollama..."

# Проверяем что ollama запущен
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama не запущен. Запустите контейнер ollama сначала."
    exit 1
fi

echo "📥 Скачиваем модель qwen2.5:6b..."
ollama pull qwen2.5:6b

if [ $? -eq 0 ]; then
    echo "✅ Модель Qwen:06 успешно загружена!"
    echo "📊 Информация о модели:"
    ollama list
else
    echo "❌ Ошибка при загрузке модели Qwen:06"
    exit 1
fi

