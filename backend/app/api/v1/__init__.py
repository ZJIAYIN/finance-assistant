"""
API v1 路由
"""
from fastapi import APIRouter

from .auth import router as auth_router
from .session import router as session_router
from .chat import router as chat_router
from .crawler import router as crawler_router
from .health import router as health_router

api_router = APIRouter(prefix="/v1")

api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(session_router, prefix="/sessions", tags=["会话"])
api_router.include_router(chat_router, prefix="/chat", tags=["对话"])
api_router.include_router(crawler_router, prefix="/crawler", tags=["爬虫"])
api_router.include_router(health_router, prefix="/health", tags=["健康检查"])
