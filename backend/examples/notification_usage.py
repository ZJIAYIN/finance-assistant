"""
消息推送模块使用示例

运行方式:
    cd backend
    python examples/notification_usage.py

请先配置环境变量或在 .env 文件中设置推送渠道配置
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.notification import (
    NotificationService,
    NotificationMessage,
    MessageType,
    DingTalkChannel,
    WeChatWorkChannel,
    EmailChannel,
)


async def example_basic_usage():
    """基础使用示例：直接注册渠道"""
    print("=" * 50)
    print("示例 1: 基础使用 - 直接注册渠道")
    print("=" * 50)

    service = NotificationService()

    # 注册钉钉渠道
    dingtalk_config = {
        "enabled": True,
        "webhook": os.getenv("DINGTALK_WEBHOOK", ""),
        "secret": os.getenv("DINGTALK_SECRET", ""),
        "at_all": False,
    }
    service.register_channel("dingtalk", DingTalkChannel(dingtalk_config))

    # 注册企业微信渠道
    wechat_config = {
        "enabled": True,
        "webhook": os.getenv("WECHAT_WORK_WEBHOOK", ""),
    }
    service.register_channel("wechat", WeChatWorkChannel(wechat_config))

    # 创建消息
    message = NotificationMessage(
        title="系统测试消息",
        content="这是一条测试消息，用于验证推送渠道配置。",
        message_type=MessageType.INFO,
    )

    # 推送到所有渠道
    results = await service.send(message)
    print(f"推送结果: {results}")


async def example_config_based():
    """基于配置的使用示例"""
    print("\n" + "=" * 50)
    print("示例 2: 基于配置注册渠道")
    print("=" * 50)

    service = NotificationService()

    # 批量从配置注册
    configs = {
        "dingtalk": {
            "enabled": True,
            "webhook": os.getenv("DINGTALK_WEBHOOK", ""),
            "secret": os.getenv("DINGTALK_SECRET", ""),
            "at_all": False,
        },
        "email": {
            "enabled": True,
            "smtp_host": os.getenv("EMAIL_SMTP_HOST", ""),
            "smtp_port": 465,
            "smtp_user": os.getenv("EMAIL_SMTP_USER", ""),
            "smtp_password": os.getenv("EMAIL_SMTP_PASSWORD", ""),
            "recipients": [os.getenv("EMAIL_RECIPIENTS", "")],
        },
    }

    service.register_from_config(configs)

    # 查看已注册渠道
    print(f"已注册渠道: {service.list_channels()}")

    # 发送不同类型的消息
    await service.send_info("信息提示", "系统运行正常")
    await service.send_success("操作成功", "数据导入完成")
    await service.send_warning("警告", "磁盘空间不足")
    await service.send_error("错误", "数据库连接失败")


async def example_specific_channel():
    """推送到指定渠道"""
    print("\n" + "=" * 50)
    print("示例 3: 推送到指定渠道")
    print("=" * 50)

    service = NotificationService()

    # 配置多个渠道
    service.register_channel(
        "dingtalk",
        DingTalkChannel({
            "enabled": True,
            "webhook": os.getenv("DINGTALK_WEBHOOK", ""),
        })
    )
    service.register_channel(
        "wechat_work",
        WeChatWorkChannel({
            "enabled": True,
            "webhook": os.getenv("WECHAT_WORK_WEBHOOK", ""),
        })
    )

    message = NotificationMessage(
        title="指定渠道消息",
        content="这条消息只发送到钉钉",
    )

    # 只发送到钉钉
    result = await service.send_to("dingtalk", message)
    print(f"钉钉推送结果: {result}")

    # 同时发送到多个渠道
    results = await service.send(
        message,
        channels=["dingtalk", "wechat_work"]
    )
    print(f"多渠道推送结果: {results}")


async def example_health_check():
    """健康检查示例"""
    print("\n" + "=" * 50)
    print("示例 4: 渠道健康检查")
    print("=" * 50)

    service = NotificationService()

    # 注册渠道
    service.register_channel(
        "dingtalk",
        DingTalkChannel({
            "enabled": True,
            "webhook": "https://oapi.dingtalk.com/robot/send?access_token=test",
        })
    )

    # 检查所有渠道健康状态
    health = await service.health_check()
    print(f"渠道健康状态: {health}")


async def example_crawler_notification():
    """爬虫任务通知示例"""
    print("\n" + "=" * 50)
    print("示例 5: 爬虫任务通知")
    print("=" * 50)

    service = NotificationService()

    # 注册至少一个渠道
    service.register_channel(
        "dingtalk",
        DingTalkChannel({
            "enabled": True,
            "webhook": os.getenv("DINGTALK_WEBHOOK", ""),
        })
    )

    # 爬取成功通知
    success_message = service.create_crawler_success_message(
        data_date="2024-01-15",
        record_count=5234
    )
    await service.send(success_message)
    print("已发送爬取成功通知")

    # 爬取失败通知
    error_message = service.create_crawler_error_message(
        data_date="2024-01-15",
        error="网络连接超时"
    )
    await service.send(error_message)
    print("已发送爬取失败通知")


async def example_price_alert():
    """价格提醒示例"""
    print("\n" + "=" * 50)
    print("示例 6: 价格提醒")
    print("=" * 50)

    service = NotificationService()

    service.register_channel(
        "wechat_work",
        WeChatWorkChannel({
            "enabled": True,
            "webhook": os.getenv("WECHAT_WORK_WEBHOOK", ""),
        })
    )

    # 创建价格提醒
    alert_message = service.create_price_alert_message(
        stock_name="比亚迪",
        stock_code="002594",
        current_price=256.80,
        alert_price=250.00,
        alert_type="上涨"
    )
    await service.send(alert_message)
    print("已发送价格提醒")


async def main():
    """运行所有示例"""
    print("消息推送模块使用示例")
    print("请先配置环境变量：DINGTALK_WEBHOOK, WECHAT_WORK_WEBHOOK 等")
    print()

    # 检查环境变量
    if not os.getenv("DINGTALK_WEBHOOK"):
        print("警告: DINGTALK_WEBHOOK 未设置，钉钉推送将失败")
    if not os.getenv("WECHAT_WORK_WEBHOOK"):
        print("警告: WECHAT_WORK_WEBHOOK 未设置，企业微信推送将失败")

    print()

    # 运行示例
    await example_basic_usage()
    await example_config_based()
    await example_specific_channel()
    await example_health_check()
    await example_crawler_notification()
    await example_price_alert()

    print("\n" + "=" * 50)
    print("所有示例运行完成")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
