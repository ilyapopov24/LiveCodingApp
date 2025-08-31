# Makefile для Android Debug Build
.PHONY: help clean build debug install test lint bundle

GRADLE := ./gradlew
APK_PATH := app/build/outputs/apk/debug/app-debug.apk
AAB_PATH := app/build/outputs/bundle/debug/app-debug.aab

help:
	@echo "Android Debug Build Makefile"
	@echo "Доступные команды:"
	@echo "  make help      - Показать эту справку"
	@echo "  make clean     - Очистить проект"
	@echo "  make build     - Собрать debug APK"
	@echo "  make debug     - Полная debug сборка (APK + AAB)"

clean:
	@echo "Очистка проекта..."
	$(GRADLE) clean
	@echo "Проект очищен"

build:
	@echo "Сборка debug APK..."
	$(GRADLE) assembleDebug
	@echo "Debug APK собран"

bundle:
	@echo "Сборка debug AAB..."
	$(GRADLE) bundleDebug
	@echo "Debug AAB собран"

debug: clean build bundle
	@echo "Полная debug сборка завершена!"

test:
	@echo "Запуск unit тестов..."
	$(GRADLE) testDebugUnitTest
	@echo "Unit тесты выполнены"

quick:
	@echo "Быстрая сборка debug APK..."
	$(GRADLE) assembleDebug --no-daemon --parallel
	@echo "Быстрая сборка завершена"

status:
	@echo "Статус сборки:"
	@if [ -f "$(APK_PATH)" ]; then echo "✓ Debug APK: $$(du -h $(APK_PATH) | cut -f1)"; else echo "✗ Debug APK: не найден"; fi
