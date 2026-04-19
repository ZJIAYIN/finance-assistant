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

from app.core.config import settings
from crawler.eastmoney import run_crawler
from crawler.vectorize import run_vectorize


scheduler = None


def daily_job():
    """每日定时任务"""
    print(f"执行每日定时任务: {__import__('datetime').datetime.now()}")

    # Step 1: 爬取数据（收盘后的数据）
    try:
        run_crawler()
        print("数据爬取完成")
    except Exception as e:
        print(f"数据爬取失败: {e}")
        return

    # Step 2: 向量化数据
    try:
        run_vectorize()
        print("向量化完成")
    except Exception as e:
        print(f"向量化失败: {e}")


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
