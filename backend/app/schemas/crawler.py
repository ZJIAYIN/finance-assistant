"""
爬虫相关 schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class CrawlTestResponse(BaseModel):
    success: bool
    message: str
    data_preview: Optional[Dict[str, Any]] = None
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
