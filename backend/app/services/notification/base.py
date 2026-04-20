"""
消息推送策略基类
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class MessageType(Enum):
    """消息类型"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class NotificationMessage:
    """通知消息数据类"""
    title: str
    content: str
    message_type: MessageType = MessageType.INFO
    timestamp: datetime = None
    extra: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.extra is None:
            self.extra = {}


class NotificationChannel(ABC):
    """
    消息推送渠道抽象基类（策略接口）

    所有具体推送渠道（钉钉、企业微信、邮件等）都需要继承此类
    并实现 send 方法
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self._enabled = config.get("enabled", True)

    @property
    def enabled(self) -> bool:
        """是否启用"""
        return self._enabled

    @abstractmethod
    async def send(self, message: NotificationMessage) -> bool:
        """
        发送消息

        Args:
            message: 要发送的消息

        Returns:
            bool: 发送是否成功
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        验证配置是否有效

        Returns:
            bool: 配置是否有效
        """
        pass

    def format_message(self, message: NotificationMessage) -> Dict[str, Any]:
        """
        格式化消息为渠道特定格式
        子类可重写此方法提供自定义格式

        Args:
            message: 原始消息

        Returns:
            格式化后的消息字典
        """
        return {
            "title": message.title,
            "content": message.content,
            "type": message.message_type.value,
            "time": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }

    async def health_check(self) -> bool:
        """
        健康检查
        检查推送渠道是否可用

        Returns:
            bool: 渠道是否健康
        """
        return self.validate_config()