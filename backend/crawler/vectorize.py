"""
将向量化任务封装为可独立运行的模块
将JSON数据向量化存入ChromaDB
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.services.rag_service import RAGService
from app.services.llm_service import LLMService


def format_index_data(index: Dict[str, Any]) -> str:
    """格式化指数数据为文本"""
    return f"""【大盘指数】{index.get('name', '')}({index.get('code', '')})
当前价格: {index.get('price', '-')}
涨跌幅: {index.get('change_pct', '-')}%
涨跌额: {index.get('change', '-')}
成交量: {index.get('volume', '-')}
成交额: {index.get('amount', '-')}"""


def format_sector_data(sector: Dict[str, Any]) -> str:
    """格式化板块数据为文本"""
    return f"""【板块行情】{sector.get('name', '')}
当前点位: {sector.get('price', '-')}
涨跌幅: {sector.get('change_pct', '-')}%
涨跌额: {sector.get('change', '-')}
成交量: {sector.get('volume', '-')}
成交额: {sector.get('amount', '-')}"""


def format_news_data(news: Dict[str, Any]) -> str:
    """格式化新闻数据为文本"""
    return f"""【财经新闻】{news.get('title', '')}
发布时间: {news.get('publish_time', '')}
摘要: {news.get('summary', '')}"""


def vectorize_json_data(date: datetime = None):
    """
    将指定日期的JSON数据向量化存入ChromaDB
    默认处理昨天的数据（t-1）
    """
    if date is None:
        date = datetime.now() - timedelta(days=1)

    filename = date.strftime("%Y-%m-%d") + ".json"
    filepath = os.path.join("./data/raw", filename)

    if not os.path.exists(filepath):
        print(f"数据文件不存在: {filepath}")
        return False

    print(f"开始向量化: {filepath}")

    # 读取JSON数据
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 准备文档
    documents = []
    metadatas = []
    ids = []

    # 处理指数数据
    for i, index in enumerate(data.get("indices", [])):
        documents.append(format_index_data(index))
        metadatas.append({
            "type": "index",
            "code": index.get("code"),
            "name": index.get("name"),
            "date": data.get("date")
        })
        ids.append(f"index_{i}")

    # 处理板块数据
    for i, sector in enumerate(data.get("sectors", [])):
        documents.append(format_sector_data(sector))
        metadatas.append({
            "type": "sector",
            "code": sector.get("code"),
            "name": sector.get("name"),
            "date": data.get("date")
        })
        ids.append(f"sector_{i}")

    # 处理新闻数据
    for i, news in enumerate(data.get("news", [])):
        documents.append(format_news_data(news))
        metadatas.append({
            "type": "news",
            "title": news.get("title"),
            "date": data.get("date")
        })
        ids.append(f"news_{i}")

    if not documents:
        print("没有数据需要向量化")
        return False

    # 存入ChromaDB
    rag_service = RAGService()
    rag_service.add_documents(
        date=date,
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"向量化完成，共 {len(documents)} 条文档")
    return True


def run_vectorize():
    """运行向量化任务（供定时任务调用）"""
    # 向量化昨天的数据
    yesterday = datetime.now() - timedelta(days=1)
    success = vectorize_json_data(yesterday)

    if success:
        # 清理旧数据
        rag_service = RAGService()
        deleted = rag_service.delete_old_collections()
        print(f"清理了 {deleted} 个过期collection")

    return success


if __name__ == "__main__":
    # 测试向量化
    run_vectorize()
