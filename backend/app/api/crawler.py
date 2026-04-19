"""
爬虫测试接口
用于手动触发爬虫和查看爬取结果
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel

from app.core.security import get_current_user_id
from crawler.eastmoney import EastMoneyCrawler, run_crawler
from crawler.vectorize import vectorize_json_data, run_vectorize

router = APIRouter()


# 响应模型
class CrawlTestResponse(BaseModel):
    success: bool
    message: str
    data_preview: Optional[dict] = None
    crawl_time: Optional[str] = None
    indices_count: int = 0
    sectors_count: int = 0
    news_count: int = 0


class VectorizeResponse(BaseModel):
    success: bool
    message: str
    date: Optional[str] = None
    documents_count: int = 0


class CrawlStatusResponse(BaseModel):
    today_crawled: bool
    today_vectorized: bool
    latest_collection: Optional[str] = None
    collections_count: int = 0


@router.post("/test", response_model=CrawlTestResponse)
def test_crawl(
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user_id)
):
    """
    手动测试爬虫（只爬取，不向量化）
    返回爬取的数据预览
    """
    try:
        crawler = EastMoneyCrawler()
        data = crawler.crawl_all()

        # 检查是否有数据
        if not data.get("indices") and not data.get("sectors") and not data.get("news"):
            return CrawlTestResponse(
                success=False,
                message="爬取失败，未获取到任何数据",
                crawl_time=datetime.now().isoformat(),
                indices_count=0,
                sectors_count=0,
                news_count=0
            )

        # 预览数据（取前2条）
        data_preview = {
            "indices": data.get("indices", [])[:2],
            "sectors": data.get("sectors", [])[:2],
            "news": data.get("news", [])[:2]
        }

        return CrawlTestResponse(
            success=True,
            message="爬取成功",
            data_preview=data_preview,
            crawl_time=data.get("crawl_time"),
            indices_count=len(data.get("indices", [])),
            sectors_count=len(data.get("sectors", [])),
            news_count=len(data.get("news", []))
        )

    except Exception as e:
        return CrawlTestResponse(
            success=False,
            message=f"爬取异常: {str(e)}",
            crawl_time=datetime.now().isoformat(),
            indices_count=0,
            sectors_count=0,
            news_count=0
        )


@router.post("/run", response_model=CrawlTestResponse)
def run_crawl_and_save(
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user_id)
):
    """
    执行完整爬虫流程：爬取 -> 保存JSON
    不入向量库（需手动调用向量化）
    """
    try:
        data = run_crawler()

        return CrawlTestResponse(
            success=True,
            message=f"数据已保存到 data/raw/{datetime.now().strftime('%Y-%m-%d')}.json",
            crawl_time=data.get("crawl_time"),
            indices_count=len(data.get("indices", [])),
            sectors_count=len(data.get("sectors", [])),
            news_count=len(data.get("news", []))
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"爬虫执行失败: {str(e)}"
        )


@router.post("/vectorize", response_model=VectorizeResponse)
def run_vectorize_manual(
    user_id: int = Depends(get_current_user_id)
):
    """
    手动执行向量化（将昨天的数据向量化入库）
    """
    try:
        from datetime import timedelta

        yesterday = datetime.now() - timedelta(days=1)
        success = vectorize_json_data(yesterday)

        if success:
            # 统计向量化文档数
            from app.services.rag_service import RAGService
            rag = RAGService()
            collection_name = rag.get_collection_name(yesterday)

            try:
                collection = rag.client.get_collection(name=collection_name)
                doc_count = collection.count()
            except:
                doc_count = 0

            return VectorizeResponse(
                success=True,
                message="向量化完成",
                date=yesterday.strftime("%Y-%m-%d"),
                documents_count=doc_count
            )
        else:
            return VectorizeResponse(
                success=False,
                message=f"向量化失败，数据文件 {yesterday.strftime('%Y-%m-%d')}.json 不存在",
                date=yesterday.strftime("%Y-%m-%d"),
                documents_count=0
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"向量化失败: {str(e)}"
        )


@router.get("/status", response_model=CrawlStatusResponse)
def get_crawl_status(
    user_id: int = Depends(get_current_user_id)
):
    """
    获取爬虫状态
    - 今日是否已爬取
    - 今日是否已向量化
    - 最新的collection名称
    """
    import os
    from app.services.rag_service import RAGService

    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # 检查今日是否已爬取
    today_file = f"./data/raw/{today}.json"
    today_crawled = os.path.exists(today_file)

    # 检查昨日是否已向量化
    rag = RAGService()
    yesterday_collection = f"market_{yesterday.replace('-', '_')}"
    collections = rag.list_collections()
    today_vectorized = yesterday_collection in collections

    # 获取最新的collection
    latest_collection = None
    market_collections = [c for c in collections if c.startswith("market_")]
    if market_collections:
        latest_collection = sorted(market_collections)[-1]

    return CrawlStatusResponse(
        today_crawled=today_crawled,
        today_vectorized=today_vectorized,
        latest_collection=latest_collection,
        collections_count=len(market_collections)
    )


@router.get("/preview/{date}")
def get_crawl_preview(
    date: str,  # 格式: 2024-04-18
    user_id: int = Depends(get_current_user_id)
):
    """
    查看指定日期的爬取数据详情
    """
    import json
    import os

    filepath = f"./data/raw/{date}.json"

    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"日期 {date} 的数据文件不存在"
        )

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {
            "date": date,
            "crawl_time": data.get("crawl_time"),
            "indices": data.get("indices", []),
            "sectors": data.get("sectors", []),
            "news": data.get("news", [])
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"读取数据失败: {str(e)}"
        )
