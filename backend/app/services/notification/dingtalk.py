"""
钉钉消息推送实现
"""
import hmac
import hashlib
import base64
import urllib.parse
import aiohttp
from typing import Any, Dict

from .base import NotificationChannel, NotificationMessage, MessageType


class DingTalkChannel(NotificationChannel):
    """
    钉钉机器人推送渠道

    配置示例:
    {
        "enabled": True,
        "webhook": "https://oapi.dingtalk.com/robot/send?access_token=xxx",
        "secret": "xxx",  # 安全设置中的加签密钥
        "at_all": False,
        "at_mobiles": ["13800138000"]
    }
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__("钉钉", config)
        self.webhook = config.get("webhook", "")
        self.secret = config.get("secret", "")
        self.at_all = config.get("at_all", False)
        self.at_mobiles = config.get("at_mobiles", [])

    def validate_config(self) -> bool:
        """验证钉钉配置"""
        if not self.enabled:
            return False
        if not self.webhook:
            return False
        if "access_token" not in self.webhook:
            return False
        return True

    def _generate_sign(self, timestamp: str) -> str:
        """生成钉钉签名"""
        if not self.secret:
            return ""
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            self.secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return sign

    def _get_message_color(self, message_type: MessageType) -> str:
        """根据消息类型获取颜色"""
        colors = {
            MessageType.INFO: "#1890ff",
            MessageType.SUCCESS: "#52c41a",
            MessageType.WARNING: "#faad14",
            MessageType.ERROR: "#f5222d",
        }
        return colors.get(message_type, "#1890ff")

    def format_message(self, message: NotificationMessage) -> Dict[str, Any]:
        """格式化为钉钉 markdown 消息"""
        color = self._get_message_color(message.message_type)

        # 构建 markdown 内容
        markdown_content = f"""### {message.title}

<div style="color: {color}">

{message.content}

</div>

---
时间：{message.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
"""

        return {
            "msgtype": "markdown",
            "markdown": {
                "title": message.title,
                "text": markdown_content
            },
            "at": {
                "atMobiles": self.at_mobiles,
                "isAtAll": self.at_all
            }
        }

    async def send(self, message: NotificationMessage) -> bool:
        """发送钉钉消息"""
        if not self.validate_config():
            return False

        import time
        timestamp = str(round(time.time() * 1000))
        sign = self._generate_sign(timestamp)

        url = self.webhook
        if self.secret:
            url = f"{self.webhook}&timestamp={timestamp}&sign={sign}"

        payload = self.format_message(message)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
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
            title="钉钉连接测试",
            content="这是一条测试消息，用于验证钉钉推送配置是否正确。",
            message_type=MessageType.INFO
        )
        return await self.send(test_message)