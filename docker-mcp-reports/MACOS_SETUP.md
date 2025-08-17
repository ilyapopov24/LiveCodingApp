# 🍎 Установка Docker на macOS

## 🚀 Быстрая установка для macOS

### Шаг 1: Скачивание Docker Desktop
1. Перейдите на [docker.com](https://www.docker.com/products/docker-desktop/)
2. Нажмите **"Download for Mac"**
3. Выберите версию для вашего процессора:
   - **Apple Silicon** (M1/M2/M3) - скачайте ARM64 версию
   - **Intel** - скачайте x64 версию

### Шаг 2: Установка
1. Откройте скачанный файл `.dmg`
2. Перетащите **Docker** в папку **Applications**
3. Откройте **Docker** из папки Applications
4. Следуйте инструкциям установщика
5. **Перезагрузите компьютер** при запросе

### Шаг 3: Первый запуск
1. Запустите **Docker Desktop** из Applications
2. Дождитесь полной загрузки (значок Docker в строке меню станет зеленым)
3. Примите лицензионное соглашение

### Шаг 4: Проверка установки
Откройте **Terminal** и выполните:
```bash
docker --version
docker-compose --version
```

## 🔧 Настройка для MCP Report Generator

### 1. Перейдите в директорию проекта
```bash
cd docker-mcp-reports
```

### 2. Настройте конфигурацию
```bash
# Копируем пример конфигурации
cp env.example .env

# Открываем для редактирования
open -e .env  # или nano .env
```

### 3. Заполните обязательные поля
```bash
# GitHub API токен
GITHUB_TOKEN=ghp_your_actual_token_here

# Gemini API ключ
GEMINI_API_KEY=your_gemini_api_key_here

# Email настройки (для Gmail)
EMAIL_PROVIDER=gmail
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SENDER_EMAIL=your_email@gmail.com
RECIPIENT_EMAILS=your_email@gmail.com
```

### 4. Запустите систему
```bash
# Делаем скрипт исполняемым
chmod +x start.sh

# Запускаем
./start.sh start
```

## 📧 Настройка Gmail для отправки

### 1. Включите двухфакторную аутентификацию
1. Перейдите в [Google Account Settings](https://myaccount.google.com/)
2. **Security** → **2-Step Verification** → включите

### 2. Создайте App Password
1. **Security** → **2-Step Verification** → **App passwords**
2. Выберите **"Mail"** из выпадающего списка
3. Нажмите **"Generate"**
4. Скопируйте 16-символьный пароль

### 3. Используйте App Password в .env
```bash
SMTP_PASSWORD=abcd efgh ijkl mnop  # ваш 16-символьный пароль
```

## 🚨 Решение проблем macOS

### Проблема: "Docker Desktop is starting..."
- Подождите 2-3 минуты после запуска
- Проверьте, что Docker Desktop полностью загрузился
- Перезапустите Docker Desktop

### Проблема: "Permission denied"
```bash
# Добавьте пользователя в группу docker
sudo dscl . -append /Groups/docker GroupMembership $USER
```

### Проблема: "Cannot connect to the Docker daemon"
- Убедитесь, что Docker Desktop запущен
- Проверьте статус в строке меню (значок должен быть зеленым)
- Перезапустите Docker Desktop

### Проблема: "Resource busy"
- Остановите все контейнеры: `docker stop $(docker ps -q)`
- Перезапустите Docker Desktop

## ⚡ Оптимизация для macOS

### Настройки Docker Desktop
1. Откройте **Docker Desktop** → **Settings**
2. **Resources** → **Advanced**:
   - **Memory**: 4GB (минимум)
   - **Swap**: 1GB
   - **Disk image size**: 64GB
3. **Resources** → **File Sharing**: добавьте папку проекта

### Настройки Terminal
```bash
# Добавьте в ~/.zshrc или ~/.bash_profile
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
```

## 🔒 Безопасность

### Рекомендации для macOS
1. **Не запускайте Docker от root**
2. **Используйте официальные образы**
3. **Регулярно обновляйте Docker Desktop**
4. **Ограничивайте доступ к файловой системе**

### Обновление Docker Desktop
1. **Docker Desktop** → **Check for Updates**
2. Скачайте и установите обновление
3. Перезапустите Docker Desktop

## 📱 Мониторинг

### Docker Desktop Dashboard
- Откройте **Docker Desktop**
- Просматривайте запущенные контейнеры
- Мониторьте использование ресурсов
- Управляйте образами и volumes

### Terminal команды
```bash
# Статус контейнеров
docker ps

# Использование ресурсов
docker stats

# Логи Docker Desktop
docker system info
```

## 🎯 Проверка работы

### 1. Тестовый контейнер
```bash
docker run hello-world
```

### 2. Проверка MCP Report Generator
```bash
# Статус
./start.sh status

# Логи
./start.sh logs

# Тестовый запуск
./start.sh test
```

### 3. Проверка конфигурации
```bash
./start.sh config
```

## 📚 Полезные ссылки

- [Docker Desktop для Mac](https://docs.docker.com/desktop/mac/)
- [Docker Hub](https://hub.docker.com/)
- [Docker Community](https://community.docker.com/)

## 🆘 Поддержка

### Если что-то не работает:
1. **Проверьте логи:** `./start.sh logs`
2. **Проверьте конфигурацию:** `./start.sh config`
3. **Перезапустите Docker Desktop**
4. **Создайте issue** в репозитории

---

**Готово!** 🎉 Docker установлен на macOS и готов к работе с MCP Report Generator!
