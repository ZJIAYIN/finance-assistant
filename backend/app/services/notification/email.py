"""
邮件消息推送实现
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any, Dict, List

from .base import NotificationChannel, NotificationMessage, MessageType


class EmailChannel(NotificationChannel):
    """
    邮件推送渠道

    配置示例:
    {
        "enabled": True,
        "smtp_host": "smtp.qq.com",
        "smtp_port": 465,
        "smtp_user": "your_email@qq.com",
        "smtp_password": "your_auth_code",
        "sender": "金融助手 <your_email@qq.com>",
        "recipients": ["user1@example.com", "user2@example.com"],
        "use_tls": True
    }
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__("邮件", config)
        self.smtp_host = config.get("smtp_host", "")
        self.smtp_port = config.get("smtp_port", 465)
        self.smtp_user = config.get("smtp_user", "")
        self.smtp_password = config.get("smtp_password", "")
        self.sender = config.get("sender", self.smtp_user)
        self.recipients = config.get("recipients", [])
        self.use_tls = config.get("use_tls", True)

    def validate_config(self) -> bool:
        """验证邮件配置"""
        if not self.enabled:
            return False
        if not all([self.smtp_host, self.smtp_user, self.smtp_password]):
            return False
        if not self.recipients:
            return False
        return True

    def _get_message_style(self, message_type: MessageType) -> Dict[str, str]:
        """根据消息类型获取样式"""
        styles = {
            MessageType.INFO: {
                "border_color": "#1890ff",
                "bg_color": "#e6f7ff",
                "title_color": "#1890ff"
            },
            MessageType.SUCCESS: {
                "border_color": "#52c41a",
                "bg_color": "#f6ffed",
                "title_color": "#52c41a"
            },
            MessageType.WARNING: {
                "border_color": "#faad14",
                "bg_color": "#fffbe6",
                "title_color": "#faad14"
            },
            MessageType.ERROR: {
                "border_color": "#f5222d",
                "bg_color": "#fff1f0",
                "title_color": "#f5222d"
            },
        }
        return styles.get(message_type, styles[MessageType.INFO])

    def format_message(self, message: NotificationMessage) -> str:
        """格式化为 HTML 邮件"""
        style = self._get_message_style(message.message_type)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .message-box {{
            border: 1px solid {style['border_color']};
            border-radius: 8px;
            padding: 20px;
            background-color: {style['bg_color']};
        }}
        .title {{
            color: {style['title_color']};
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
        }}
        .content {{ color: #333; line-height: 1.6; margin-bottom: 15px; }}
        .footer {{ color: #999; font-size: 12px; border-top: 1px solid #eee; padding-top: 10px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="message-box">
            <div class="title">{message.title}</div>
            <div class="content">{message.content.replace(chr(10), '<br>')}</div>
        </div>
        <div class="footer">
            发送时间：{message.timestamp.strftime("%Y-%m-%d %H:%M:%S")}<br>
            本邮件由金融助手系统自动发送
        </div>
    </div>
</body>
</html>"""
        return html

    async def send(self, message: NotificationMessage) -> bool:
        """发送邮件"""
        if not self.validate_config():
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[金融助手] {message.title}"
            msg['From'] = self.sender
            msg['To'] = ", ".join(self.recipients)

            # 添加 HTML 内容
            html_content = self.format_message(message)
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            # 发送邮件
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=self.use_tls,
                timeout=30
            )
            return True
        except Exception:
            return False

    async def send_to(self, recipients: List[str], message: NotificationMessage) -> bool:
        """
        发送邮件到指定收件人

        Args:
            recipients: 收件人列表
            message: 消息
        """
        if not self.validate_config():
            return False

        original_recipients = self.recipients
        self.recipients = recipients

        try:
            result = await self.send(message)
        finally:
            self.recipients = original_recipients

        return result

    async def health_check(self) -> bool:
        """健康检查 - 尝试连接 SMTP 服务器"""
        try:
            await aiosmtplib.connect(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=self.use_tls,
                timeout=10
            )
            return True
        except Exception:
            return False