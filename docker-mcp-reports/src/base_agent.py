#!/usr/bin/env python3
"""
Base Agent - базовый класс для всех агентов в мультиагентной системе
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"

@dataclass
class AgentMessage:
    sender: str
    receiver: str
    message_type: str
    data: Any
    timestamp: float
    correlation_id: str

class BaseAgent(ABC):
    """Базовый класс для всех агентов в мультиагентной системе"""
    
    def __init__(self, name: str):
        self.name = name
        self.status = AgentStatus.IDLE
        self.next_agents: List['BaseAgent'] = []
        self.previous_agents: List['BaseAgent'] = []
        self.message_queue: List[AgentMessage] = []
        self.other_agents: Dict[str, 'BaseAgent'] = {}
        self.correlation_id = None
        self.context = {}
        
        logger.info(f"Агент {self.name} инициализирован")
    
    def add_next_agent(self, agent: 'BaseAgent'):
        """Добавляет следующего агента в цепочку"""
        self.next_agents.append(agent)
        agent.previous_agents.append(self)
        self.other_agents[agent.name] = agent
        logger.info(f"Агент {self.name} подключен к {agent.name}")
    
    def send_message(self, to_agent: str, message_type: str, data: Any):
        """Отправляет сообщение другому агенту"""
        message = AgentMessage(
            sender=self.name,
            receiver=to_agent,
            message_type=message_type,
            data=data,
            timestamp=asyncio.get_event_loop().time(),
            correlation_id=self.correlation_id or f"{self.name}_{asyncio.get_event_loop().time()}"
        )
        
        if to_agent in self.other_agents:
            self.other_agents[to_agent].receive_message(message)
            logger.info(f"Агент {self.name} отправил сообщение {message_type} агенту {to_agent}")
        else:
            logger.error(f"Агент {to_agent} не найден для отправки сообщения от {self.name}")
    
    def receive_message(self, message: AgentMessage):
        """Получает сообщение от другого агента"""
        self.message_queue.append(message)
        logger.info(f"Агент {self.name} получил сообщение {message.message_type} от {message.sender}")
        asyncio.create_task(self.process_messages())
    
    async def process_messages(self):
        """Обрабатывает очередь сообщений"""
        while self.message_queue:
            message = self.message_queue.pop(0)
            await self.handle_message(message)
    
    async def handle_message(self, message: AgentMessage):
        """Обрабатывает конкретное сообщение"""
        self.correlation_id = message.correlation_id
        logger.info(f"Агент {self.name} обрабатывает сообщение {message.message_type}")
        
        # Каждый агент реализует свою логику обработки сообщений
        await self.process_message(message)
    
    @abstractmethod
    async def process_message(self, message: AgentMessage):
        """Абстрактный метод для обработки сообщений"""
        pass
    
    @abstractmethod
    async def process(self, data: Any) -> Any:
        """Абстрактный метод для основной обработки данных"""
        pass
    
    def can_continue(self, data: Any) -> bool:
        """Определяет, может ли агент продолжить обработку"""
        return True
    
    def should_stop(self, data: Any) -> bool:
        """Определяет, должен ли агент остановить обработку"""
        return False
    
    async def process_chain(self, data: Any) -> Any:
        """Обрабатывает данные и передает следующему агенту"""
        try:
            self.status = AgentStatus.PROCESSING
            logger.info(f"Агент {self.name} начинает обработку")
            
            # Обрабатываем данные
            result = await self.process(data)
            
            # Проверяем, нужно ли продолжить
            if self.should_stop(result):
                logger.info(f"Агент {self.name} останавливает цепочку")
                self.status = AgentStatus.IDLE
                return result
            
            # Передаем следующему агенту
            if self.next_agents and self.can_continue(result):
                next_agent = self.next_agents[0]
                logger.info(f"Агент {self.name} передает данные агенту {next_agent.name}")
                return await next_agent.process_chain(result)
            else:
                logger.info(f"Агент {self.name} завершает цепочку")
                self.status = AgentStatus.IDLE
                return result
                
        except Exception as e:
            logger.error(f"Ошибка в агенте {self.name}: {str(e)}")
            self.status = AgentStatus.ERROR
            raise
