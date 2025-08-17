#!/bin/bash

# MCP Report Generator - Скрипт управления
# Автор: MCP Report Generator Team
# Версия: 1.0.0

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка зависимостей
check_dependencies() {
    print_info "Проверка зависимостей..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker не установлен. Установите Docker и попробуйте снова."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
        exit 1
    fi
    
    print_success "Все зависимости установлены"
}

# Проверка конфигурации
check_config() {
    print_info "Проверка конфигурации..."
    
    if [ ! -f ".env" ]; then
        print_warning "Файл .env не найден. Создаю из примера..."
        if [ -f "env.example" ]; then
            cp env.example .env
            print_warning "Файл .env создан из env.example. Пожалуйста, отредактируйте его!"
            print_warning "Заполните обязательные поля: GITHUB_TOKEN, GEMINI_API_KEY, SMTP_*"
            exit 1
        else
            print_error "Файл env.example не найден. Проверьте структуру проекта."
            exit 1
        fi
    fi
    
    # Проверяем обязательные переменные
    source .env
    
    if [ -z "$GITHUB_TOKEN" ] || [ "$GITHUB_TOKEN" = "your_github_token_here" ]; then
        print_error "GITHUB_TOKEN не настроен в .env файле"
        exit 1
    fi
    
    if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "your_gemini_api_key_here" ]; then
        print_error "GEMINI_API_KEY не настроен в .env файле"
        exit 1
    fi
    
    if [ -z "$SMTP_USERNAME" ] || [ -z "$SMTP_PASSWORD" ] || [ -z "$SENDER_EMAIL" ] || [ -z "$RECIPIENT_EMAILS" ]; then
        print_error "Email настройки неполные в .env файле"
        exit 1
    fi
    
    print_success "Конфигурация проверена"
}

# Создание директорий
create_directories() {
    print_info "Создание необходимых директорий..."
    
    mkdir -p logs data
    print_success "Директории созданы"
}

# Сборка образа
build_image() {
    print_info "Сборка Docker образа..."
    
    docker-compose build --no-cache
    print_success "Образ собран"
}

# Запуск сервиса
start_service() {
    print_info "Запуск MCP Report Generator..."
    
    docker-compose up -d
    print_success "Сервис запущен"
}

# Остановка сервиса
stop_service() {
    print_info "Остановка MCP Report Generator..."
    
    docker-compose down
    print_success "Сервис остановлен"
}

# Перезапуск сервиса
restart_service() {
    print_info "Перезапуск MCP Report Generator..."
    
    docker-compose restart
    print_success "Сервис перезапущен"
}

# Просмотр статуса
show_status() {
    print_info "Статус сервисов:"
    docker-compose ps
    
    echo ""
    print_info "Использование ресурсов:"
    docker stats --no-stream mcp-report-generator 2>/dev/null || print_warning "Контейнер не запущен"
}

# Просмотр логов
show_logs() {
    local service=${1:-mcp-report-generator}
    local lines=${2:-50}
    
    print_info "Показ последних $lines строк логов для $service:"
    docker-compose logs --tail=$lines -f $service
}

# Проверка конфигурации в контейнере
check_container_config() {
    print_info "Проверка конфигурации в контейнере..."
    
    docker-compose run --rm mcp-report-generator config
}

# Тестовый запуск
test_run() {
    print_info "Тестовый запуск MCP Report Generator..."
    
    docker-compose run --rm mcp-report-generator test
}

# Очистка
cleanup() {
    print_info "Очистка системы..."
    
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_success "Очистка завершена"
}

# Обновление
update() {
    print_info "Обновление системы..."
    
    git pull origin main
    docker-compose down
    docker-compose up -d --build
    print_success "Система обновлена"
}

# Помощь
show_help() {
    echo "MCP Report Generator - Скрипт управления"
    echo ""
    echo "Использование: $0 [КОМАНДА]"
    echo ""
    echo "Команды:"
    echo "  start       - Запуск сервиса"
    echo "  stop        - Остановка сервиса"
    echo "  restart     - Перезапуск сервиса"
    echo "  status      - Показать статус"
    echo "  logs        - Показать логи"
    echo "  config      - Проверить конфигурацию"
    echo "  test        - Тестовый запуск"
    echo "  build       - Сборка образа"
    echo "  cleanup     - Очистка системы"
    echo "  update      - Обновление системы"
    echo "  help        - Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0 start                    # Запуск сервиса"
    echo "  $0 logs                     # Показать логи"
    echo "  $0 logs 100                 # Показать последние 100 строк"
    echo "  $0 test                     # Тестовый запуск"
    echo ""
}

# Основная логика
main() {
    local command=${1:-help}
    
    case $command in
        start)
            check_dependencies
            check_config
            create_directories
            build_image
            start_service
            show_status
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            show_status
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs $2 $3
            ;;
        config)
            check_container_config
            ;;
        test)
            check_dependencies
            check_config
            create_directories
            test_run
            ;;
        build)
            check_dependencies
            build_image
            ;;
        cleanup)
            cleanup
            ;;
        update)
            update
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Неизвестная команда: $command"
            show_help
            exit 1
            ;;
    esac
}

# Проверяем, что скрипт запущен из правильной директории
if [ ! -f "docker-compose.yml" ]; then
    print_error "Скрипт должен быть запущен из директории с docker-compose.yml"
    exit 1
fi

# Запуск основной логики
main "$@"
