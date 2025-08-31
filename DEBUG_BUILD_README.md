# 🚀 Android Debug Build Pipeline

Полноценный пайплайн для автоматизированной debug-сборки Android приложения с CI/CD интеграцией.

## 📁 Структура пайплайна

```
.github/workflows/
├── android-debug-build.yml    # Полный пайплайн с тестами
└── quick-debug-build.yml      # Быстрая сборка без тестов

build-debug.sh                 # Локальный скрипт сборки
gradle-debug.properties        # Оптимизированные настройки Gradle
Makefile                       # Makefile для удобной сборки
```

## 🎯 Возможности

### ✅ **GitHub Actions CI/CD**
- Автоматическая сборка при push/PR
- Кэширование Gradle зависимостей
- Запуск unit и instrumented тестов
- Генерация отчетов (lint, test)
- Загрузка артефактов (APK, AAB)

### 🚀 **Локальная сборка**
- Bash скрипт с цветным выводом
- Makefile с удобными командами
- Оптимизированные настройки Gradle
- Автоматическая установка на устройство

## 🚀 Быстрый старт

### 1. **Локальная сборка (рекомендуется для разработки)**

```bash
# Простая сборка
./build-debug.sh

# Сборка без тестов
./build-debug.sh --skip-tests

# Сборка с установкой на устройство
./build-debug.sh --install

# Справка
./build-debug.sh --help
```

### 2. **Использование Makefile**

```bash
# Показать справку
make help

# Быстрая сборка
make quick

# Полная сборка
make debug

# Сборка с тестами
make all

# Установка на устройство
make install
```

### 3. **Прямые Gradle команды**

```bash
# Debug APK
./gradlew assembleDebug

# Debug AAB
./gradlew bundleDebug

# Unit тесты
./gradlew testDebugUnitTest

# Lint проверка
./gradlew lintDebug
```

## 🔧 Настройка

### **Переменные окружения**
Создайте `.env` файл в корне проекта:

```bash
# Android SDK
export ANDROID_HOME=/path/to/android/sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# Java
export JAVA_HOME=/path/to/java
export PATH=$JAVA_HOME/bin:$PATH
```

### **Gradle оптимизации**
Используйте `gradle-debug.properties` для ускорения сборки:

```bash
# Копирование настроек
cp gradle-debug.properties gradle.properties

# Или использование через параметр
./gradlew assembleDebug -Dorg.gradle.jvmargs="-Xmx4096m"
```

## 📊 Мониторинг сборки

### **GitHub Actions**
- Перейдите в `Actions` → `Android Debug Build`
- Просматривайте логи в реальном времени
- Скачивайте артефакты после успешной сборки

### **Локальная сборка**
```bash
# Статус сборки
make status

# Информация о проекте
make info

# Проверка зависимостей
./build-debug.sh --help
```

## 🐛 Устранение проблем

### **Частые ошибки**

1. **"Gradle daemon not responding"**
   ```bash
   make restart-daemon
   # или
   ./gradlew --stop && ./gradlew --start
   ```

2. **"Out of memory"**
   ```bash
   # Увеличьте память в gradle.properties
   org.gradle.jvmargs=-Xmx4096m
   ```

3. **"SDK not found"**
   ```bash
   # Установите ANDROID_HOME
   export ANDROID_HOME=/path/to/android/sdk
   ```

4. **"Permission denied"**
   ```bash
   chmod +x gradlew
   chmod +x build-debug.sh
   ```

### **Очистка кэша**
```bash
# Очистка Gradle кэша
make clean-cache

# Очистка проекта
make clean

# Полная очистка
./gradlew clean cleanBuildCache
```

## 📱 Установка на устройство

### **Автоматическая установка**
```bash
# Подключите устройство и включите USB Debugging
./build-debug.sh --install

# Или через Makefile
make install
```

### **Ручная установка**
```bash
# Сборка
make build

# Установка
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

## 🔄 Интеграция с IDE

### **Android Studio**
1. Откройте проект
2. Синхронизируйте Gradle файлы
3. Используйте `Build` → `Make Project` для быстрой сборки

### **VS Code**
1. Установите Android extension pack
2. Используйте команды в терминале
3. Настройте задачи в `.vscode/tasks.json`

## 📈 Производительность

### **Оптимизации по умолчанию**
- ✅ Параллельная сборка
- ✅ Gradle кэширование
- ✅ Incremental compilation
- ✅ Daemon режим
- ✅ Configuration cache

### **Дополнительные оптимизации**
```bash
# Использование всех ядер
./gradlew assembleDebug --parallel --max-workers=8

# Отключение daemon для CI
./gradlew assembleDebug --no-daemon

# Очистка кэша при проблемах
./gradlew clean cleanBuildCache
```

## 🚀 Расширение пайплайна

### **Добавление новых задач**
1. Отредактируйте `.github/workflows/android-debug-build.yml`
2. Добавьте новые шаги в `jobs.build.steps`
3. Настройте условия запуска

### **Кастомные команды**
```bash
# Добавьте в Makefile
custom-task:
	@echo "Выполнение кастомной задачи..."
	# Ваш код здесь
```

## 📞 Поддержка

При возникновении проблем:

1. **Проверьте логи**: `./gradlew assembleDebug --info`
2. **Очистите кэш**: `make clean-cache`
3. **Перезапустите daemon**: `make restart-daemon`
4. **Проверьте зависимости**: `./build-debug.sh --help`

## 📝 Changelog

- **v1.0.0** - Базовый пайплайн с CI/CD
- **v1.1.0** - Добавлен Makefile и оптимизации
- **v1.2.0** - Улучшенный bash скрипт
- **v1.3.0** - Оптимизированные Gradle настройки

---

**🎉 Готово!** Теперь у вас есть полноценный пайплайн для debug-сборки Android приложения.
