#!/bin/bash

# MCP Report Generator - Скрипт управления
# Поддерживает как основной сервис, так и MCP сервер

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Проверяем наличие Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker не установлен. Установите Docker и попробуйте снова."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker не запущен. Запустите Docker и попробуйте снова."
        exit 1
    fi
}

# Проверяем наличие docker-compose
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
        exit 1
    fi
}

# Проверяем наличие .env файла
check_env_file() {
    if [ ! -f .env ]; then
        print_warning "Файл .env не найден. Создайте его на основе .env.example"
        if [ -f .env.example ]; then
            print_message "Копирую .env.example в .env..."
            cp .env.example .env
            print_warning "Отредактируйте .env файл с вашими настройками"
        else
            print_error "Файл .env.example не найден. Создайте .env файл вручную."
            exit 1
        fi
    fi
}

# Функция для запуска основного сервиса
start_main_service() {
    print_header "Запуск основного сервиса MCP Report Generator"
    docker-compose up -d mcp-report-generator
    print_message "Основной сервис запущен"
}

# Функция для запуска MCP сервера
start_mcp_server() {
    print_header "Запуск MCP сервера для Cursor"
    docker-compose up -d mcp-server
    print_message "MCP сервер запущен"
}

# Функция для остановки сервисов
stop_services() {
    print_header "Остановка всех сервисов"
    docker-compose down
    print_message "Все сервисы остановлены"
}

# Функция для перезапуска сервисов
restart_services() {
    print_header "Перезапуск сервисов"
    docker-compose restart
    print_message "Сервисы перезапущены"
}

# Функция для просмотра логов
show_logs() {
    local service=${1:-"all"}
    
    if [ "$service" = "all" ]; then
        print_header "Логи всех сервисов"
        docker-compose logs -f
    else
        print_header "Логи сервиса: $service"
        docker-compose logs -f "$service"
    fi
}

# Функция для сборки образов
build_images() {
    print_header "Сборка Docker образов"
    docker-compose build --no-cache
    print_message "Образы собраны"
}

# Функция для проверки статуса
check_status() {
    print_header "Статус сервисов"
    docker-compose ps
    
    echo ""
    print_header "Использование ресурсов"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# Функция для тестирования MCP сервера
test_mcp() {
    print_header "Тестирование MCP сервера"
    
    # Запускаем MCP сервер в фоне
    docker-compose run --rm mcp-server mcp-test
    
    print_message "MCP тестирование завершено"
}

# Функция для очистки
cleanup() {
    print_header "Очистка Docker ресурсов"
    
    # Останавливаем и удаляем контейнеры
    docker-compose down -v
    
    # Удаляем неиспользуемые образы
    docker image prune -f
    
    # Удаляем неиспользуемые volumes
    docker volume prune -f
    
    print_message "Очистка завершена"
}

# Функция для показа справки
show_help() {
    echo "MCP Report Generator - Скрипт управления"
    echo ""
    echo "Использование: $0 [КОМАНДА]"
    echo ""
    echo "Команды:"
    echo "  start           - Запуск всех сервисов"
    echo "  stop            - Остановка всех сервисов"
    echo "  restart         - Перезапуск всех сервисов"
    echo "  status          - Показать статус сервисов"
    echo "  logs [СЕРВИС]   - Показать логи (всех или конкретного сервиса)"
    echo "  build           - Пересобрать Docker образы"
    echo "  test-mcp        - Тестирование MCP функциональности"
    echo "  cleanup         - Очистка Docker ресурсов"
    echo "  help            - Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0 start                    # Запуск всех сервисов"
    echo "  $0 logs mcp-server          # Логи MCP сервера"
    echo "  $0 logs mcp-report-generator # Логи основного сервиса"
    echo ""
}

# Основная логика
main() {
    # Проверяем зависимости
    check_docker
    check_docker_compose
    check_env_file
    
    case "${1:-start}" in
        "start")
            start_main_service
            start_mcp_server
            print_message "Все сервисы запущены"
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "status")
            check_status
            ;;
        "logs")
            show_logs "$2"
            ;;
        "build")
            build_images
            ;;
        "test-mcp")
            test_mcp
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Неизвестная команда: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Запуск основной функции
main "$@"
