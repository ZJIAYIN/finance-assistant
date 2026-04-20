"""
健康检查接口
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("")
def health_check():
    """健康检查"""
    return {"status": "ok", "service": "finance-assistant-api"}


@router.get("/ready")
def readiness_check():
    """就绪检查（可扩展检查数据库等）"""
    return {"ready": True}
