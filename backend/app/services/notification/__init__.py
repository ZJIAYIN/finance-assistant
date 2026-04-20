"""
消息推送模块

使用策略模式支持多平台消息推送
"""
from .base import NotificationChannel, NotificationMessage
from .service import NotificationService
from .dingtalk import DingTalkChannel
from .wechat_work import WeChatWorkChannel
from .email import EmailChannel

__all__ = [
    "NotificationChannel",
    "NotificationMessage",
    "NotificationService",
    "DingTalkChannel",
    "WeChatWorkChannel",
    "EmailChannel",
]