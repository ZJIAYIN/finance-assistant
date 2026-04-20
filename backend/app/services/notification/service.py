"""
消息推送服务（策略上下文）

管理多个推送渠道，提供统一的推送接口
"""
from typing import Any, Dict, List, Optional, Type
import asyncio

from .base import NotificationChannel, NotificationMessage, MessageType
from .dingtalk import DingTalkChannel
from .wechat_work import WeChatWorkChannel
from .email import EmailChannel


class NotificationService:
    """
    消息推送服务

    作为策略模式的上下文，管理多个推送渠道
    支持同时向多个渠道推送消息

    使用示例:
        service = NotificationService()
        service.register_channel("dingtalk", DingTalkChannel(config))
        service.register_channel("email", EmailChannel(config))

        # 推送到所有渠道
        await service.send(NotificationMessage(
            title="测试消息",
            content="这是一条测试消息"
        ))

        # 推送到指定渠道
        await service.send_to("dingtalk", message)
    """

    # 支持的渠道类型映射
    CHANNEL_TYPES: Dict[str, Type[NotificationChannel]] = {
        "dingtalk": DingTalkChannel,
        "wechat_work": WeChatWorkChannel,
        "email": EmailChannel,
    }

    def __init__(self):
        self._channels: Dict[str, NotificationChannel] = {}
        self._default_channel: Optional[str] = None

    def register_channel(self, name: str, channel: NotificationChannel,
                         is_default: bool = False) -> None:
        """
        注册推送渠道

        Args:
            name: 渠道名称
            channel: 渠道实例
            is_default: 是否设为默认渠道
        """
        self._channels[name] = channel
        if is_default or self._default_channel is None:
            self._default_channel = name

    def register_from_config(self, configs: Dict[str, Dict[str, Any]]) -> None:
        """
        从配置批量注册渠道

        Args:
            configs: 配置字典，格式为 {channel_name: config}

        示例:
            configs = {
                "dingtalk": {
                    "enabled": True,
                    "webhook": "xxx",
                    "secret": "xxx"
                },
                "email": {
                    "enabled": True,
                    "smtp_host": "smtp.qq.com",
                    ...
                }
            }
        """
        for name, config in configs.items():
            if not config.get("enabled", True):
                continue

            channel_class = self.CHANNEL_TYPES.get(name)
            if channel_class:
                try:
                    channel = channel_class(config)
                    if channel.validate_config():
                        self.register_channel(name, channel)
                except Exception:
                    # 配置无效，跳过
                    continue

    def unregister_channel(self, name: str) -> bool:
        """
        注销推送渠道

        Args:
            name: 渠道名称

        Returns:
            bool: 是否成功注销
        """
        if name in self._channels:
            del self._channels[name]
            if self._default_channel == name:
                self._default_channel = next(iter(self._channels), None)
            return True
        return False

    def get_channel(self, name: str) -> Optional[NotificationChannel]:
        """
        获取指定渠道

        Args:
            name: 渠道名称

        Returns:
            渠道实例或 None
        """
        return self._channels.get(name)

    def list_channels(self) -> List[str]:
        """
        获取所有已注册渠道名称

        Returns:
            渠道名称列表
        """
        return list(self._channels.keys())

    def get_enabled_channels(self) -> List[str]:
        """
        获取所有启用的渠道名称

        Returns:
            启用的渠道名称列表
        """
        return [name for name, channel in self._channels.items() if channel.enabled]

    async def send(self, message: NotificationMessage,
                   channels: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        发送消息

        Args:
            message: 要发送的消息
            channels: 指定渠道列表，None 表示发送到所有启用的渠道

        Returns:
            发送结果，格式为 {channel_name: success}
        """
        target_channels = channels or self.get_enabled_channels()

        if not target_channels:
            return {}

        tasks = []
        for name in target_channels:
            channel = self._channels.get(name)
            if channel and channel.enabled:
                tasks.append((name, channel.send(message)))

        results = {}
        for name, task in tasks:
            try:
                results[name] = await task
            except Exception:
                results[name] = False

        return results

    async def send_to(self, channel_name: str,
                      message: NotificationMessage) -> bool:
        """
        发送消息到指定渠道

        Args:
            channel_name: 渠道名称
            message: 要发送的消息

        Returns:
            bool: 发送是否成功
        """
        channel = self._channels.get(channel_name)
        if not channel or not channel.enabled:
            return False

        try:
            return await channel.send(message)
        except Exception:
            return False

    async def send_info(self, title: str, content: str,
                        channels: Optional[List[str]] = None) -> Dict[str, bool]:
        """发送信息类型消息"""
        message = NotificationMessage(
            title=title,
            content=content,
            message_type=MessageType.INFO
        )
        return await self.send(message, channels)

    async def send_success(self, title: str, content: str,
                           channels: Optional[List[str]] = None) -> Dict[str, bool]:
        """发送成功类型消息"""
        message = NotificationMessage(
            title=title,
            content=content,
            message_type=MessageType.SUCCESS
        )
        return await self.send(message, channels)

    async def send_warning(self, title: str, content: str,
                           channels: Optional[List[str]] = None) -> Dict[str, bool]:
        """发送警告类型消息"""
        message = NotificationMessage(
            title=title,
            content=content,
            message_type=MessageType.WARNING
        )
        return await self.send(message, channels)

    async def send_error(self, title: str, content: str,
                         channels: Optional[List[str]] = None) -> Dict[str, bool]:
        """发送错误类型消息"""
        message = NotificationMessage(
            title=title,
            content=content,
            message_type=MessageType.ERROR
        )
        return await self.send(message, channels)

    async def health_check(self) -> Dict[str, bool]:
        """
        检查所有渠道健康状态

        Returns:
            检查结果，格式为 {channel_name: is_healthy}
        """
        results = {}
        for name, channel in self._channels.items():
            try:
                results[name] = await channel.health_check()
            except Exception:
                results[name] = False
        return results

    def create_crawler_success_message(self, data_date: str,
                                       record_count: int) -> NotificationMessage:
        """
        创建爬虫成功消息

        Args:
            data_date: 数据日期
            record_count: 记录数量

        Returns:
            通知消息
        """
        return NotificationMessage(
            title="数据爬取完成",
            content=f"日期：{data_date}\n共抓取 {record_count} 条记录",
            message_type=MessageType.SUCCESS
        )

    def create_crawler_error_message(self, data_date: str,
                                     error: str) -> NotificationMessage:
        """
        创建爬虫失败消息

        Args:
            data_date: 数据日期
            error: 错误信息

        Returns:
            通知消息
        """
        return NotificationMessage(
            title="数据爬取失败",
            content=f"日期：{data_date}\n错误：{error}",
            message_type=MessageType.ERROR
        )

    def create_price_alert_message(self, stock_name: str, stock_code: str,
                                   current_price: float,
                                   alert_price: float,
                                   alert_type: str = "上涨") -> NotificationMessage:
        """
        创建价格提醒消息

        Args:
            stock_name: 股票名称
            stock_code: 股票代码
            current_price: 当前价格
            alert_price: 提醒价格
            alert_type: 提醒类型（上涨/下跌）

        Returns:
            通知消息
        """
        return NotificationMessage(
            title=f"价格提醒：{stock_name} ({stock_code})",
            content=f"当前价格：{current_price}\n提醒价格：{alert_price}\n类型：{alert_type}触发",
            message_type=MessageType.WARNING
        )