"""
企业微信消息推送实现
"""
import aiohttp
from typing import Any, Dict

from .base import NotificationChannel, NotificationMessage, MessageType


class WeChatWorkChannel(NotificationChannel):
    """
    企业微信机器人推送渠道

    配置示例:
    {
        "enabled": True,
        "webhook": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx",
        "mentioned_list": ["@all"],  # 或 ["UserID1", "UserID2"]
        "mentioned_mobile_list": ["13800138000"]
    }
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__("企业微信", config)
        self.webhook = config.get("webhook", "")
        self.mentioned_list = config.get("mentioned_list", [])
        self.mentioned_mobile_list = config.get("mentioned_mobile_list", [])

    def validate_config(self) -> bool:
        """验证企业微信配置"""
        if not self.enabled:
            return False
        if not self.webhook:
            return False
        if "key=" not in self.webhook:
            return False
        return True

    def _get_message_emoji(self, message_type: MessageType) -> str:
        """根据消息类型获取 emoji"""
        emojis = {
            MessageType.INFO: "ℹ️",
            MessageType.SUCCESS: "✅",
            MessageType.WARNING: "⚠️",
            MessageType.ERROR: "❌",
        }
        return emojis.get(message_type, "ℹ️")

    def format_message(self, message: NotificationMessage) -> Dict[str, Any]:
        """格式化为企业微信 markdown 消息"""
        emoji = self._get_message_emoji(message.message_type)

        content = f"""{emoji} **{message.title}**

{message.content}

时间：{message.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
"""

        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }

        # 添加 @ 功能
        if self.mentioned_list:
            payload["mentioned_list"] = self.mentioned_list
        if self.mentioned_mobile_list:
            payload["mentioned_mobile_list"] = self.mentioned_mobile_list

        return payload

    async def send(self, message: NotificationMessage) -> bool:
        """发送企业微信消息"""
        if not self.validate_config():
            return False

        payload = self.format_message(message)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("errcode") == 0:
                            return True
                    return False
        except Exception:
            return False

    async def send_text_card(self, title: str, description: str, url: str,
                            btntxt: str = "查看详情") -> bool:
        """
        发送文本卡片消息

        Args:
            title: 标题
            description: 描述
            url: 点击跳转链接
            btntxt: 按钮文字
        """
        if not self.validate_config():
            return False

        payload = {
            "msgtype": "textcard",
            "textcard": {
                "title": title,
                "description": description,
                "url": url,
                "btntxt": btntxt
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("errcode") == 0:
                            return True
                    return False
        except Exception:
            return False

    async def send_news(self, articles: list) -> bool:
        """
        发送图文消息

        Args:
            articles: 文章列表，每项为 {"title": "", "description": "", "url": "", "picurl": ""}
        """
        if not self.validate_config():
            return False

        payload = {
            "msgtype": "news",
            "news": {
                "articles": articles
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("errcode") == 0:
                            return True
                    return False
        except Exception:
            return False

    async def health_check(self) -> bool:
        """健康检查 - 发送测试消息"""
        test_message = NotificationMessage(
            title="企业微信连接测试",
            content="这是一条测试消息，用于验证企业微信推送配置是否正确。",
            message_type=MessageType.INFO
        )
        return await self.send(test_message)