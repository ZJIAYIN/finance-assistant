"""
API路由
"""
from fastapi import APIRouter

from .v1 import api_router as v1_router

# 主路由，包含所有版本
api_router = APIRouter(prefix="/api")
api_router.include_router(v1_router)

__all__ = ["api_router"]
