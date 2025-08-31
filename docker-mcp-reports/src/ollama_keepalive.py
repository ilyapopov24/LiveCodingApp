#!/usr/bin/env python3
"""
Keepalive скрипт для Ollama MCP сервера
"""

import subprocess
import sys
import time
import signal
import os

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    print("Получен сигнал завершения, останавливаю Ollama MCP сервер...", file=sys.stderr)
    sys.exit(0)

def main():
    """Основная функция keepalive"""
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Запуск Ollama MCP сервера...", file=sys.stderr)
    
    try:
        # Запускаем MCP сервер
        process = subprocess.Popen(
            [sys.executable, "src/ollama_mcp_server.py"],
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
            cwd="/app"
        )
        
        # Ждем завершения процесса
        return_code = process.wait()
        
        if return_code != 0:
            print(f"Ollama MCP сервер завершился с кодом {return_code}", file=sys.stderr)
            sys.exit(return_code)
            
    except KeyboardInterrupt:
        print("Получен сигнал прерывания", file=sys.stderr)
        if 'process' in locals():
            process.terminate()
            process.wait()
    except Exception as e:
        print(f"Ошибка при запуске Ollama MCP сервера: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

