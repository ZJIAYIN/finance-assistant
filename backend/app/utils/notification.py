"""
通知服务初始化工具
"""
from typing import Dict, Any

from app.core.config import settings
from app.services.notification import NotificationService


async def init_notification_service() -> NotificationService:
    """
    初始化通知服务
    从配置中读取并注册所有启用的推送渠道
    """
    service = NotificationService()

    # 构建渠道配置
    configs: Dict[str, Dict[str, Any]] = {
        "dingtalk": {
            "enabled": settings.DINGTALK_ENABLED,
            "webhook": settings.DINGTALK_WEBHOOK,
            "secret": settings.DINGTALK_SECRET,
            "at_all": settings.DINGTALK_AT_ALL,
            "at_mobiles": [m.strip() for m in settings.DINGTALK_AT_MOBILES.split(",") if m.strip()],
        },
        "wechat_work": {
            "enabled": settings.WECHAT_WORK_ENABLED,
            "webhook": settings.WECHAT_WORK_WEBHOOK,
            "mentioned_list": [m.strip() for m in settings.WECHAT_WORK_MENTIONED.split(",") if m.strip()],
        },
        "email": {
            "enabled": settings.EMAIL_ENABLED,
            "smtp_host": settings.EMAIL_SMTP_HOST,
            "smtp_port": settings.EMAIL_SMTP_PORT,
            "smtp_user": settings.EMAIL_SMTP_USER,
            "smtp_password": settings.EMAIL_SMTP_PASSWORD,
            "sender": settings.EMAIL_SENDER or settings.EMAIL_SMTP_USER,
            "recipients": [r.strip() for r in settings.EMAIL_RECIPIENTS.split(",") if r.strip()],
            "use_tls": True,
        },
    }

    service.register_from_config(configs)

    return service


# 全局通知服务实例
_notification_service: NotificationService = None


async def get_notification_service() -> NotificationService:
    """获取通知服务实例（单例）"""
    global _notification_service
    if _notification_service is None:
        _notification_service = await init_notification_service()
    return _notification_service


def get_notification_config() -> Dict[str, Any]:
    """获取通知配置信息（用于展示）"""
    return {
        "channels": {
            "dingtalk": {
                "enabled": settings.DINGTALK_ENABLED,
                "configured": bool(settings.DINGTALK_WEBHOOK),
            },
            "wechat_work": {
                "enabled": settings.WECHAT_WORK_ENABLED,
                "configured": bool(settings.WECHAT_WORK_WEBHOOK),
            },
            "email": {
                "enabled": settings.EMAIL_ENABLED,
                "configured": bool(settings.EMAIL_SMTP_HOST and settings.EMAIL_SMTP_USER),
            },
        }
    }