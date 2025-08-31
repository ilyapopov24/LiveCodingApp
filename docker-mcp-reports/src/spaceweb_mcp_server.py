#!/usr/bin/env python3
"""
Spaceweb VPS MCP Server
Управление VPS на Spaceweb через API
"""

import json
import logging
import os
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SpacewebMCPServer:
    """MCP сервер для управления VPS на Spaceweb"""
    
    def __init__(self):
        # Загружаем переменные окружения
        load_dotenv('docker.env')
        
        # Инициализируем API токен
        self.api_token = os.getenv('SPACEWEB_TOKEN')
        if not self.api_token:
            raise ValueError("SPACEWEB_TOKEN не настроен в docker.env файле!")
        
        self.api_base_url = "https://api.sweb.ru"
        logger.info("Spaceweb API настроен успешно")
        
        self.tools = [
            {
                "name": "get-available-config",
                "description": "Получает доступные планы VPS, дистрибутивы ОС и датацентры",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "list-vps",
                "description": "Получает список существующих VPS",
                "inputSchema": {
                    "type": "object", 
                    "properties": {},
                    "required": []
                }
            },
            {
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
                        },
                        "sshKey": {
                            "type": "string",
                            "description": "Публичный SSH-ключ (опционально)"
                        },
                        "sshKeyName": {
                            "type": "string",
                            "description": "Имя SSH-ключа (опционально)"
                        },
                        "privateIp": {
                            "type": "boolean",
                            "description": "Подключить к локальной сети (опционально)"
                        },
                        "monitoringPlanId": {
                            "type": "integer",
                            "description": "ID плана мониторинга (опционально)"
                        },
                        "monitoringContactId": {
                            "type": "integer",
                            "description": "ID контакта мониторинга (опционально)"
                        },
                        "remoteBackupId": {
                            "type": "integer",
                            "description": "ID бэкапа (опционально)"
                        },
                        "ipCount": {
                            "type": "integer",
                            "description": "Количество IP-адресов (опционально)"
                        },
                        "protectedIps": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "Массив ID тарифов защищенных IP (опционально)"
                        }
                    },
                    "required": ["vpsPlanId", "distributiveId"]
                }
            }
        ]

    def list_tools(self) -> List[Dict[str, Any]]:
        """Возвращает список доступных инструментов"""
        logger.info(f"Возвращено {len(self.tools)} инструментов")
        return self.tools

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Вызывает указанный инструмент с аргументами"""
        logger.info(f"Вызов инструмента: {tool_name} с аргументами: {arguments}")
        
        try:
            if tool_name == "get-available-config":
                return self.get_available_config()
            elif tool_name == "list-vps":
                return self.list_vps()
            elif tool_name == "create-vps":
                return self.create_vps(arguments)
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Неизвестный инструмент: {tool_name}"
                        }
                    ]
                }
        except Exception as e:
            logger.error(f"Ошибка выполнения инструмента {tool_name}: {str(e)}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"💥 Ошибка выполнения инструмента {tool_name}: {str(e)}"
                    }
                ]
            }

    def get_available_config(self) -> Dict[str, Any]:
        """Получает доступные конфигурации VPS"""
        try:
            logger.info("Получение доступных конфигураций VPS")
            
            # JSON-RPC 2.0 payload для получения конфигурации
            payload = {
                "jsonrpc": "2.0",
                "method": "getAvailableConfig",
                "params": {},
                "id": "get_config"
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.post(
                f"{self.api_base_url}/vps",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                if "error" in response_data:
                    error_info = response_data["error"]
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"❌ Ошибка получения конфигурации: {error_info.get('message', 'N/A')}"
                            }
                        ]
                    }
                
                result = response_data.get("result", {})
                result_text = "📋 Доступные конфигурации VPS:\n\n"
                
                # Тарифные планы
                if "vpsPlans" in result:
                    result_text += "💰 **Тарифные планы:**\n"
                    for plan in result["vpsPlans"]:
                        result_text += f"  • ID: {plan.get('id')} - {plan.get('name')} "
                        result_text += f"({plan.get('cpu_cores')} CPU, {plan.get('ram')} RAM, "
                        result_text += f"{plan.get('volume_disk')} GB) - {plan.get('price_per_month', 0)} руб/мес\n"
                    result_text += "\n"
                
                # Дистрибутивы (правильные ID из osPanel)
                if "osPanel" in result:
                    result_text += "💿 **Дистрибутивы ОС:**\n"
                    # Группируем по OS для читаемости
                    os_groups = {}
                    for dist in result["osPanel"]:
                        os_id = dist.get('os')
                        if os_id not in os_groups:
                            os_groups[os_id] = []
                        os_groups[os_id].append(dist)
                    
                    for os_id, distributions in os_groups.items():
                        # Находим название ОС из selectOs
                        os_name = "Unknown OS"
                        if "selectOs" in result:
                            for os_info in result["selectOs"]:
                                if str(os_info.get('id')) == str(os_id):
                                    os_name = os_info.get('name', 'Unknown OS')
                                    break
                        
                        result_text += f"  **{os_name} (os_id: {os_id}):**\n"
                        for dist in distributions:
                            panel_name = "No Panel"
                            if "selectPanel" in result:
                                for panel in result["selectPanel"]:
                                    if str(panel.get('id')) == str(dist.get('panel')):
                                        panel_name = panel.get('name', 'Unknown Panel')
                                        break
                            result_text += f"    • ID: {dist.get('distributive')} - {panel_name}\n"
                    result_text += "\n"
                
                # Датацентры
                if "datacenters" in result:
                    result_text += "🏢 **Датацентры:**\n"
                    for dc in result["datacenters"]:
                        result_text += f"  • ID: {dc.get('id')} - {dc.get('location')} ({dc.get('site_name')})\n"
                    result_text += "\n"
                
                result_text += "ℹ️ Используйте эти **distributive ID** для создания VPS с помощью create-vps"
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result_text
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Ошибка HTTP: {response.status_code}\n{response.text}"
                        }
                    ]
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения конфигурации: {str(e)}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"💥 Ошибка получения конфигурации: {str(e)}"
                    }
                ]
            }

    def list_vps(self) -> Dict[str, Any]:
        """Получает список существующих VPS"""
        try:
            logger.info("Получение списка VPS")
            
            # JSON-RPC 2.0 payload для получения списка VPS
            payload = {
                "jsonrpc": "2.0", 
                "method": "index",
                "params": {},
                "id": "list_vps"
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.post(
                f"{self.api_base_url}/vps",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                if "error" in response_data:
                    error_info = response_data["error"]
                    return {
                        "content": [
                            {
                                "type": "text", 
                                "text": f"❌ Ошибка получения списка VPS: {error_info.get('message', 'N/A')}"
                            }
                        ]
                    }
                
                vps_list = response_data.get("result", [])
                
                if not vps_list:
                    result_text = "📭 У вас пока нет VPS серверов"
                else:
                    result_text = f"🖥️ Ваши VPS серверы ({len(vps_list)} шт.):\n\n"
                    
                    for vps in vps_list:
                        result_text += f"**{vps.get('name', 'N/A')}**\n"
                        result_text += f"  • ID: {vps.get('billingId', 'N/A')}\n"
                        result_text += f"  • План: {vps.get('plan_name', 'N/A')}\n"
                        result_text += f"  • ОС: {vps.get('os_distribution', 'N/A')}\n"
                        result_text += f"  • IP: {vps.get('ip', 'N/A')}\n"
                        result_text += f"  • Статус: {'🟢 Активен' if vps.get('active') else '🔴 Неактивен'}\n"
                        result_text += f"  • Создан: {vps.get('ts_create', 'N/A')}\n\n"
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result_text
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Ошибка HTTP: {response.status_code}\n{response.text}"
                        }
                    ]
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения списка VPS: {str(e)}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"💥 Ошибка получения списка VPS: {str(e)}"
                    }
                ]
            }

    def create_vps(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Создает новый VPS на Spaceweb"""
        try:
            vps_plan_id = arguments.get("vpsPlanId")
            distributive_id = arguments.get("distributiveId")
            datacenter = arguments.get("datacenter")
            alias = arguments.get("alias")
            
            # Валидация обязательных параметров
            if not all([vps_plan_id, distributive_id]):
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "❌ Отсутствуют обязательные параметры: vpsPlanId, distributiveId"
                        }
                    ]
                }
            
            logger.info(f"Создание VPS: {alias} с планом {vps_plan_id} и дистрибутивом {distributive_id}")
            
            # Подготовка данных для JSON-RPC API
            params = {
                "vpsPlanId": int(vps_plan_id),
                "distributiveId": int(distributive_id)
            }
            
            # Добавляем опциональные базовые параметры если они есть
            if datacenter is not None:
                params["datacenter"] = int(datacenter)
            if alias is not None:
                params["alias"] = str(alias)
            
            # Добавляем опциональные параметры если они есть
            optional_params = [
                "sshKey", "sshKeyName", "privateIp", "monitoringPlanId", 
                "monitoringContactId", "remoteBackupId", "ipCount", "protectedIps"
            ]
            
            for param in optional_params:
                if param in arguments and arguments[param] is not None:
                    if param in ["monitoringPlanId", "monitoringContactId", "remoteBackupId", "ipCount"]:
                        params[param] = int(arguments[param])
                    elif param == "protectedIps":
                        # Обрабатываем массив ID тарифов защищенных IP
                        if isinstance(arguments[param], list):
                            params[param] = [int(ip) for ip in arguments[param]]
                        else:
                            params[param] = [int(arguments[param])]
                    else:
                        params[param] = arguments[param]
            
            # JSON-RPC 2.0 payload
            payload = {
                "jsonrpc": "2.0",
                "method": "create",
                "params": params
            }
            
            # Отправка запроса к API Spaceweb
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.post(
                f"{self.api_base_url}/vps",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                import json
                
                # Проверяем на ошибки в JSON-RPC ответе
                if "error" in response_data:
                    error_info = response_data["error"]
                    error_text = f"❌ Ошибка создания VPS\n\n"
                    error_text += f"🔢 Код: {error_info.get('code', 'N/A')}\n"
                    error_text += f"💬 Сообщение: {error_info.get('message', 'N/A')}\n"
                    
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": error_text
                            }
                        ]
                    }
                
                # Успешный ответ
                vps_name = response_data.get("result", "N/A")
                result_text = f"✅ VPS успешно создан!\n\n"
                result_text += f"🖥️ Имя VPS: {vps_name}\n"
                result_text += f"📛 Алиас: {alias}\n"
                result_text += f"💰 План: {vps_plan_id}\n"
                result_text += f"💿 Дистрибутив: {distributive_id}\n"
                result_text += f"🏢 Датацентр: {datacenter}\n"
                
                if "sshKey" in params:
                    result_text += f"🔑 SSH-ключ добавлен\n"
                if "monitoringPlanId" in params:
                    result_text += f"📊 Мониторинг: план {params['monitoringPlanId']}\n"
                if "ipCount" in params:
                    result_text += f"🌐 IP адресов: {params['ipCount']}\n"
                    
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result_text
                        }
                    ]
                }
            else:
                error_text = f"❌ Ошибка HTTP запроса\n\n"
                error_text += f"📊 Статус: {response.status_code}\n"
                
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_info = error_data['error']
                        error_text += f"🔢 Код: {error_info.get('code', 'N/A')}\n"
                        error_text += f"💬 Сообщение: {error_info.get('message', 'N/A')}\n"
                    else:
                        error_text += f"💬 Ответ: {error_data}\n"
                except:
                    error_text += f"💬 Ответ: {response.text}\n"
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": error_text
                        }
                    ]
                }
                
        except requests.exceptions.Timeout:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "⏰ Превышен таймаут запроса к Spaceweb API"
                    }
                ]
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к Spaceweb API: {str(e)}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"🌐 Ошибка соединения с Spaceweb API: {str(e)}"
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Неожиданная ошибка при создании VPS: {str(e)}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"💥 Неожиданная ошибка: {str(e)}"
                    }
                ]
            }

def main():
    """Главная функция для запуска MCP сервера"""
    server = SpacewebMCPServer()
    logger.info("Spaceweb MCP Server запущен")

if __name__ == "__main__":
    main()

