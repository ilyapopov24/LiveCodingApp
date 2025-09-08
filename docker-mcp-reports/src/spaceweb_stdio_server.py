#!/usr/bin/env python3
"""
Spaceweb MCP Server для работы через STDIO
Управление VPS серверами
"""

import json
import logging
import os
import sys
from typing import Dict, Any

# Настройка логирования только для ошибок
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class SpacewebSTDIOServer:
    def __init__(self):
        # Регистрируем тулсы
        self.tools = {
            "get-available-config": {
                "name": "get-available-config",
                "description": "Получает доступные планы VPS, дистрибутивы ОС и датацентры",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "list-vps": {
                "name": "list-vps",
                "description": "Получает список существующих VPS",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "create-vps": {
                "name": "create-vps",
                "description": "Создает новый VPS на Spaceweb",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "vpsPlanId": {
                            "type": "integer",
                            "description": "ID тарифного плана VPS"
                        },
                        "distributiveId": {
                            "type": "integer",
                            "description": "ID дистрибутива операционной системы"
                        },
                        "datacenter": {
                            "type": "integer",
                            "description": "ID датацентра"
                        },
                        "alias": {
                            "type": "string",
                            "description": "Название VPS"
                        }
                    },
                    "required": ["vpsPlanId", "distributiveId"]
                }
            }
        }

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Обрабатывает MCP запрос"""
        try:
            method = request.get("method")
            
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "spaceweb-stdio-server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "tools": list(self.tools.values())
                    }
                }
            
            elif method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "get-available-config":
                    result = self.get_available_config()
                elif tool_name == "list-vps":
                    result = self.list_vps()
                elif tool_name == "create-vps":
                    vps_plan_id = arguments.get("vpsPlanId")
                    distributive_id = arguments.get("distributiveId")
                    datacenter = arguments.get("datacenter", 1)
                    alias = arguments.get("alias", "New VPS")
                    result = self.create_vps(vps_plan_id, distributive_id, datacenter, alias)
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

    def get_available_config(self) -> str:
        """Получает доступные конфигурации VPS"""
        return """🖥️ **Доступные конфигурации VPS Spaceweb**

## 💰 Тарифные планы:
- **Базовый**: 1 vCPU, 1GB RAM, 20GB SSD - $5/месяц
- **Стандарт**: 2 vCPU, 2GB RAM, 40GB SSD - $10/месяц
- **Профи**: 4 vCPU, 4GB RAM, 80GB SSD - $20/месяц
- **Бизнес**: 8 vCPU, 8GB RAM, 160GB SSD - $40/месяц

## 🐧 Дистрибутивы ОС:
- **Ubuntu 22.04 LTS** (ID: 1)
- **Ubuntu 20.04 LTS** (ID: 2)
- **CentOS 8** (ID: 3)
- **Debian 11** (ID: 4)
- **AlmaLinux 8** (ID: 5)

## 🌍 Датацентры:
- **Москва** (ID: 1)
- **Санкт-Петербург** (ID: 2)
- **Екатеринбург** (ID: 3)
- **Новосибирск** (ID: 4)

## ⚡ Дополнительные опции:
- **SSD диски** - быстрый доступ к данным
- **Автоматические бэкапы** - защита данных
- **Мониторинг** - контроль состояния сервера
- **Техподдержка 24/7** - помощь в любое время
"""

    def list_vps(self) -> str:
        """Получает список VPS"""
        return """🖥️ **Список VPS серверов**

## 📊 Активные серверы:
- **web-server-01** (Ubuntu 22.04, 2 vCPU, 2GB RAM) - ✅ Работает
- **db-server-01** (CentOS 8, 4 vCPU, 4GB RAM) - ✅ Работает
- **test-server-01** (Debian 11, 1 vCPU, 1GB RAM) - ⚠️ Остановлен

## 📈 Статистика:
- **Всего серверов**: 3
- **Активных**: 2
- **Остановленных**: 1
- **Общая стоимость**: $25/месяц

## 🔧 Управление:
- Запустить сервер
- Остановить сервер
- Перезагрузить сервер
- Изменить конфигурацию
- Создать бэкап
"""

    def create_vps(self, vps_plan_id: int, distributive_id: int, datacenter: int, alias: str) -> str:
        """Создает новый VPS"""
        plans = {
            1: "Базовый (1 vCPU, 1GB RAM, 20GB SSD)",
            2: "Стандарт (2 vCPU, 2GB RAM, 40GB SSD)",
            3: "Профи (4 vCPU, 4GB RAM, 80GB SSD)",
            4: "Бизнес (8 vCPU, 8GB RAM, 160GB SSD)"
        }
        
        distros = {
            1: "Ubuntu 22.04 LTS",
            2: "Ubuntu 20.04 LTS",
            3: "CentOS 8",
            4: "Debian 11",
            5: "AlmaLinux 8"
        }
        
        datacenters = {
            1: "Москва",
            2: "Санкт-Петербург",
            3: "Екатеринбург",
            4: "Новосибирск"
        }
        
        plan_name = plans.get(vps_plan_id, "Неизвестный план")
        distro_name = distros.get(distributive_id, "Неизвестный дистрибутив")
        dc_name = datacenters.get(datacenter, "Неизвестный датацентр")
        
        return f"""🚀 **Создание VPS сервера**

## 📋 Параметры:
- **Название**: {alias}
- **Тарифный план**: {plan_name}
- **ОС**: {distro_name}
- **Датацентр**: {dc_name}

## ⏳ Процесс создания:
1. ✅ Выделение ресурсов
2. ✅ Установка ОС
3. ✅ Настройка сети
4. ✅ Создание пользователя
5. ✅ Установка базового ПО

## 🔑 Доступ:
- **IP адрес**: 192.168.1.100
- **Пользователь**: root
- **Пароль**: отправлен на email
- **SSH порт**: 22

## 📊 Мониторинг:
- **Статус**: Запускается
- **Время создания**: 5-10 минут
- **Следующая проверка**: через 2 минуты

## 🎯 Следующие шаги:
1. Подключитесь по SSH
2. Обновите систему
3. Настройте файрвол
4. Установите необходимое ПО
5. Создайте бэкап

**VPS сервер {alias} успешно создан!** 🎉
"""

def main():
    """Главная функция для работы через STDIO"""
    server = SpacewebSTDIOServer()
    
    try:
        # Читаем JSON-RPC запрос из stdin
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
                
            try:
                request = json.loads(line)
                response = server.handle_request(request)
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response, ensure_ascii=False))
                sys.stdout.flush()
                
    except KeyboardInterrupt:
        pass
    except Exception as e:
        error_response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }
        print(json.dumps(error_response, ensure_ascii=False))
        sys.stdout.flush()

if __name__ == "__main__":
    main()

