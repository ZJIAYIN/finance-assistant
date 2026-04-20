"""
定时任务调度器
每日自动爬取数据并更新向量库
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio

from app.core.config import settings
from crawler.eastmoney import run_crawler
from crawler.vectorize import run_vectorize
from app.utils.notification import init_notification_service


scheduler = None


async def async_daily_job():
    """异步每日定时任务"""
    from datetime import datetime

    print(f"执行每日定时任务: {datetime.now()}")

    # 初始化通知服务
    notification_service = await init_notification_service()

    data_date = datetime.now().strftime("%Y-%m-%d")
    record_count = 0

    # Step 1: 爬取数据（收盘后的数据）
    try:
        result = run_crawler()
        print("数据爬取完成")

        # 发送成功通知
        message = notification_service.create_crawler_success_message(
            data_date=data_date,
            record_count=result.get("count", 0) if isinstance(result, dict) else 0
        )
        await notification_service.send(message)
    except Exception as e:
        print(f"数据爬取失败: {e}")
        # 发送失败通知
        message = notification_service.create_crawler_error_message(
            data_date=data_date,
            error=str(e)
        )
        await notification_service.send(message)
        return

    # Step 2: 向量化数据
    try:
        run_vectorize()
        print("向量化完成")
        # 发送向量化完成通知
        await notification_service.send_success(
            title="数据向量化完成",
            content=f"日期：{data_date}\n数据已成功向量化并存入向量库"
        )
    except Exception as e:
        print(f"向量化失败: {e}")
        # 发送向量化失败通知
        await notification_service.send_error(
            title="数据向量化失败",
            content=f"日期：{data_date}\n错误：{str(e)}"
        )


def daily_job():
    """每日定时任务入口（同步包装）"""
    asyncio.run(async_daily_job())


def start_scheduler():
    """启动定时任务调度器"""
    global scheduler

    scheduler = BackgroundScheduler()

    # 每日指定时间执行
    hour, minute = settings.CRAWL_TIME.split(":")
    scheduler.add_job(
        daily_job,
        trigger=CronTrigger(hour=int(hour), minute=int(minute)),
        id="daily_crawl_job",
        replace_existing=True
    )

    scheduler.start()
    print(f"定时任务已启动，每日 {settings.CRAWL_TIME} 执行")

    return scheduler


def stop_scheduler():
    """停止定时任务"""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        print("定时任务已停止")


if __name__ == "__main__":
    # 测试：立即执行一次
    print("测试模式：立即执行一次任务")
    daily_job()
