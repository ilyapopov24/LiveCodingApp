#!/bin/bash

# Android Debug Build Script
# Автоматизированная сборка debug версии приложения

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции логирования
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка зависимостей
check_dependencies() {
    log_info "Проверка зависимостей..."
    
    if ! command -v java &> /dev/null; then
        log_error "Java не установлена!"
        exit 1
    fi
    
    if ! command -v adb &> /dev/null; then
        log_warning "ADB не найден. Установите Android SDK для полной функциональности."
    fi
    
    if [ ! -f "gradlew" ]; then
        log_error "gradlew не найден! Убедитесь, что вы в корневой папке проекта."
        exit 1
    fi
    
    log_success "Зависимости проверены"
}

# Очистка проекта
clean_project() {
    log_info "Очистка проекта..."
    ./gradlew clean
    log_success "Проект очищен"
}

# Сборка debug APK
build_debug_apk() {
    log_info "Сборка debug APK..."
    ./gradlew assembleDebug --no-daemon --parallel
    log_success "Debug APK собран"
}

# Сборка debug AAB
build_debug_aab() {
    log_info "Сборка debug AAB..."
    ./gradlew bundleDebug --no-daemon --parallel
    log_success "Debug AAB собран"
}

# Запуск unit тестов
run_unit_tests() {
    log_info "Запуск unit тестов..."
    ./gradlew testDebugUnitTest
    log_success "Unit тесты выполнены"
}

# Запуск lint проверки
run_lint() {
    log_info "Запуск lint проверки..."
    ./gradlew lintDebug
    log_success "Lint проверка завершена"
}

# Установка на устройство (если подключено)
install_on_device() {
    if command -v adb &> /dev/null; then
        log_info "Проверка подключенных устройств..."
        if adb devices | grep -q "device$"; then
            log_info "Установка APK на устройство..."
            adb install -r app/build/outputs/apk/debug/app-debug.apk
            log_success "APK установлен на устройство"
        else
            log_warning "Устройство не подключено или не авторизовано"
        fi
    fi
}

# Показать информацию о сборке
show_build_info() {
    log_info "=== ИНФОРМАЦИЯ О СБОРКЕ ==="
    
    APK_PATH="app/build/outputs/apk/debug/app-debug.apk"
    AAB_PATH="app/build/outputs/bundle/debug/app-debug.aab"
    
    if [ -f "$APK_PATH" ]; then
        APK_SIZE=$(du -h "$APK_PATH" | cut -f1)
        log_success "Debug APK: $APK_PATH (размер: $APK_SIZE)"
    else
        log_error "Debug APK не найден!"
    fi
    
    if [ -f "$AAB_PATH" ]; then
        AAB_SIZE=$(du -h "$AAB_PATH" | cut -f1)
        log_success "Debug AAB: $AAB_PATH (размер: $AAB_SIZE)"
    else
        log_error "Debug AAB не найден!"
    fi
    
    # Показать версию приложения
    if [ -f "app/build.gradle.kts" ]; then
        VERSION=$(grep "versionName" app/build.gradle.kts | sed 's/.*versionName = "\(.*\)".*/\1/')
        VERSION_CODE=$(grep "versionCode" app/build.gradle.kts | sed 's/.*versionCode = \([0-9]*\).*/\1/')
        log_info "Версия: $VERSION (код: $VERSION_CODE)"
    fi
}

# Основная функция
main() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Android Debug Build Script${NC}"
    echo -e "${BLUE}================================${NC}"
    
    START_TIME=$(date +%s)
    
    # Проверка аргументов
    SKIP_TESTS=false
    SKIP_LINT=false
    INSTALL_DEVICE=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --skip-lint)
                SKIP_LINT=true
                shift
                ;;
            --install)
                INSTALL_DEVICE=true
                shift
                ;;
            --help)
                echo "Использование: $0 [опции]"
                echo "Опции:"
                echo "  --skip-tests    Пропустить unit тесты"
                echo "  --skip-lint     Пропустить lint проверку"
                echo "  --install       Установить APK на подключенное устройство"
                echo "  --help          Показать эту справку"
                exit 0
                ;;
            *)
                log_error "Неизвестная опция: $1"
                echo "Используйте --help для справки"
                exit 1
                ;;
        esac
    done
    
    log_info "Начало сборки debug версии..."
    
    # Выполнение этапов сборки
    check_dependencies
    clean_project
    build_debug_apk
    build_debug_aab
    
    if [ "$SKIP_TESTS" = false ]; then
        run_unit_tests
    else
        log_warning "Unit тесты пропущены"
    fi
    
    if [ "$SKIP_LINT" = false ]; then
        run_lint
    else
        log_warning "Lint проверка пропущена"
    fi
    
    if [ "$INSTALL_DEVICE" = true ]; then
        install_on_device
    fi
    
    show_build_info
    
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    log_success "Сборка завершена за $DURATION секунд!"
    log_info "APK файл: app/build/outputs/apk/debug/app-debug.apk"
    log_info "AAB файл: app/build/outputs/bundle/debug/app-debug.aab"
}

# Запуск скрипта
main "$@"
