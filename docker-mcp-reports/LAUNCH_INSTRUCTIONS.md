# 🚀 Инструкция по запуску MCP Report Generator

## ⚡ Быстрый старт (5 минут)

### Шаг 1: Установите Docker
```bash
# macOS: скачайте Docker Desktop с docker.com
# Windows: скачайте Docker Desktop с docker.com
# Linux: выполните команды ниже
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

### Шаг 2: Перейдите в директорию проекта
```bash
cd docker-mcp-reports
```

### Шаг 3: Настройте конфигурацию
```bash
# Копируем пример
cp env.example .env

# Редактируем настройки
nano .env  # или любой текстовый редактор
```

**Обязательные поля для заполнения:**
```bash
GITHUB_TOKEN=ghp_your_actual_token_here
GEMINI_API_KEY=your_gemini_api_key_here
EMAIL_PROVIDER=gmail
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SENDER_EMAIL=your_email@gmail.com
RECIPIENT_EMAILS=your_email@gmail.com
```

### Шаг 4: Запустите систему
```bash
# Делаем скрипт исполняемым
chmod +x start.sh

# Запускаем
./start.sh start
```

### Шаг 5: Проверьте работу
```bash
# Статус
./start.sh status

# Логи
./start.sh logs

# Тестовый запуск
./start.sh test
```

## 🎯 Что происходит дальше

✅ **Система запущена** - контейнер работает в фоне  
✅ **Cron настроен** - отчеты будут генерироваться каждый день в 9:00 UTC  
✅ **Логи доступны** - все действия записываются в `./logs/`  
✅ **Email настроен** - отчеты будут приходить на указанный адрес  

## 📧 Первый отчет

Первый отчет будет сгенерирован **завтра в 9:00 UTC** (или в другое время, если настроили).

**Хотите получить отчет прямо сейчас?**
```bash
./start.sh test
```

## 🔧 Управление системой

```bash
./start.sh start      # Запуск
./start.sh stop       # Остановка  
./start.sh restart    # Перезапуск
./start.sh status     # Статус
./start.sh logs       # Логи
./start.sh test       # Тестовый запуск
./start.sh config     # Проверка настроек
./start.sh help       # Справка
```

## 🚨 Если что-то не работает

### Проверьте Docker
```bash
docker --version
docker-compose --version
```

### Проверьте конфигурацию
```bash
./start.sh config
```

### Посмотрите логи
```bash
./start.sh logs
```

### Перезапустите систему
```bash
./start.sh restart
```

## 📚 Подробная документация

- **README.md** - полная документация
- **QUICKSTART.md** - быстрый старт
- **DOCKER_INSTALL.md** - установка Docker
- **MACOS_SETUP.md** - установка на macOS
- **PROJECT_SUMMARY.md** - сводка проекта

## 🆘 Нужна помощь?

1. **Проверьте логи:** `./start.sh logs`
2. **Проверьте конфигурацию:** `./start.sh config`
3. **Создайте issue** в репозитории
4. **Опишите проблему** с логами

---

**Готово!** 🎉 Теперь вы будете получать автоматические отчеты о вашем GitHub профиле каждый день!
