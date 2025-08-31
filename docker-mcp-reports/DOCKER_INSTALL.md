# Установка Docker

## 🐳 Что такое Docker

**Docker** - это платформа для разработки, доставки и запуска приложений в изолированных контейнерах. В нашем случае он позволит:

- ✅ **Автоматизировать** процесс генерации отчетов
- ✅ **Запускать** код без установки всех зависимостей на компьютер
- ✅ **Планировать** выполнение задач (раз в день)
- ✅ **Отправлять** отчеты на email автоматически

## 📋 Системные требования

### macOS
- macOS 10.15 (Catalina) или новее
- Минимум 4GB RAM
- 20GB свободного места на диске

### Windows
- Windows 10/11 Pro, Enterprise или Education
- WSL 2 включен
- Минимум 4GB RAM
- 20GB свободного места на диске

### Linux
- Ubuntu 18.04+ или аналогичный дистрибутив
- Минимум 4GB RAM
- 20GB свободного места на диске

## 🚀 Установка Docker

### macOS

#### 1. Скачивание Docker Desktop
1. Перейдите на [docker.com](https://www.docker.com/products/docker-desktop/)
2. Нажмите "Download for Mac"
3. Выберите версию для вашего процессора (Intel или Apple Silicon)

#### 2. Установка
1. Откройте скачанный файл `.dmg`
2. Перетащите Docker в папку Applications
3. Запустите Docker из Applications
4. Следуйте инструкциям установщика

#### 3. Проверка установки
```bash
# Откройте Terminal и выполните:
docker --version
docker-compose --version
```

### Windows

#### 1. Подготовка системы
1. **Включите WSL 2:**
   ```powershell
   # Запустите PowerShell от администратора
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```

2. **Перезагрузите компьютер**

3. **Установите WSL 2:**
   ```powershell
   wsl --install
   ```

#### 2. Скачивание Docker Desktop
1. Перейдите на [docker.com](https://www.docker.com/products/docker-desktop/)
2. Нажмите "Download for Windows"
3. Скачайте установщик

#### 3. Установка
1. Запустите установщик от имени администратора
2. Следуйте инструкциям
3. При запросе выберите "Use WSL 2 instead of Hyper-V"

#### 4. Проверка установки
```cmd
# Откройте Command Prompt и выполните:
docker --version
docker-compose --version
```

### Linux (Ubuntu)

#### 1. Обновление системы
```bash
sudo apt update
sudo apt upgrade -y
```

#### 2. Установка зависимостей
```bash
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
```

#### 3. Добавление GPG ключа Docker
```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

#### 4. Добавление репозитория Docker
```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

#### 5. Установка Docker
```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

#### 6. Добавление пользователя в группу docker
```bash
sudo usermod -aG docker $USER
# Перезайдите в систему или выполните:
newgrp docker
```

#### 7. Запуск Docker
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

#### 8. Проверка установки
```bash
docker --version
docker compose version
```

## 🔧 Установка Docker Compose (если не установлен)

### Автоматическая установка (рекомендуется)
```bash
# Docker Compose уже включен в Docker Desktop для macOS/Windows
# Для Linux используйте встроенную версию:
docker compose version
```

### Ручная установка (если нужно)
```bash
# Скачивание Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Делаем исполняемым
sudo chmod +x /usr/local/bin/docker-compose

# Проверяем установку
docker-compose --version
```

## ✅ Проверка установки

### Тест Docker
```bash
# Запуск тестового контейнера
docker run hello-world
```

### Тест Docker Compose
```bash
# Создание тестового файла
echo 'version: "3.8"
services:
  hello:
    image: hello-world' > test-compose.yml

# Запуск теста
docker-compose -f test-compose.yml up

# Очистка
rm test-compose.yml
```

## 🚨 Решение проблем

### macOS

#### Проблема: "Docker Desktop is starting..."
- Подождите 1-2 минуты после запуска
- Проверьте, что Docker Desktop полностью загрузился
- Перезапустите Docker Desktop

#### Проблема: "Permission denied"
```bash
# Добавьте пользователя в группу docker
sudo dscl . -append /Groups/docker GroupMembership $USER
```

### Windows

#### Проблема: "WSL 2 is not enabled"
```powershell
# Включите WSL 2
wsl --set-default-version 2
```

#### Проблема: "Docker Desktop failed to start"
- Перезагрузите компьютер
- Запустите Docker Desktop от имени администратора
- Проверьте, что WSL 2 работает

### Linux

#### Проблема: "Permission denied"
```bash
# Добавьте пользователя в группу docker
sudo usermod -aG docker $USER
# Перезайдите в систему
```

#### Проблема: "Cannot connect to the Docker daemon"
```bash
# Запустите Docker
sudo systemctl start docker
sudo systemctl enable docker
```

## 🔒 Безопасность

### Рекомендации
1. **Не запускайте Docker от root** (кроме Linux)
2. **Используйте официальные образы**
3. **Регулярно обновляйте Docker**
4. **Ограничивайте доступ к Docker daemon**

### Обновление Docker
```bash
# macOS/Windows: обновляйте через Docker Desktop
# Linux:
sudo apt update
sudo apt upgrade docker-ce docker-ce-cli containerd.io
```

## 📚 Дополнительные ресурсы

### Официальная документация
- [Docker Documentation](https://docs.docker.com/)
- [Docker Desktop](https://docs.docker.com/desktop/)
- [Docker Compose](https://docs.docker.com/compose/)

### Полезные ссылки
- [Docker Hub](https://hub.docker.com/)
- [Docker Community](https://community.docker.com/)
- [Docker GitHub](https://github.com/docker)

### Видеоуроки
- [Docker Tutorial for Beginners](https://www.youtube.com/watch?v=pTFZFxd4hOI)
- [Docker Compose Tutorial](https://www.youtube.com/watch?v=DM65_JyGxUk)

## 🎯 Следующие шаги

После успешной установки Docker:

1. **Перейдите в директорию проекта:**
   ```bash
   cd docker-mcp-reports
   ```

2. **Настройте конфигурацию:**
   ```bash
   cp env.example .env
   # Отредактируйте .env файл
   ```

3. **Запустите систему:**
   ```bash
   ./start.sh start
   ```

4. **Проверьте работу:**
   ```bash
   ./start.sh status
   ./start.sh logs
   ```

---

**Поздравляем!** 🎉 Docker установлен и готов к работе с MCP Report Generator!
