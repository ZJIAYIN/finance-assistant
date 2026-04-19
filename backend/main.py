"""
金融投资智能助手 - FastAPI后端入口
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api import api_router


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    app = FastAPI(
        title=settings.APP_NAME,
        description="基于RAG的金融投资智能助手",
        version="1.0.0",
        debug=settings.DEBUG
    )

    # CORS配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应该限制域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(api_router, prefix="/api")

    @app.on_event("startup")
    async def startup_event():
        """应用启动时的初始化"""
        # 确保数据目录存在
        os.makedirs("./data/raw", exist_ok=True)
        os.makedirs("./data/chroma", exist_ok=True)
        os.makedirs("./db", exist_ok=True)

        # 初始化数据库
        init_db()
        print("数据库初始化完成")

        # 启动定时任务（如果需要）
        # from crawler.scheduler import start_scheduler
        # start_scheduler()

    @app.get("/")
    def root():
        return {
            "message": "金融投资智能助手API服务",
            "version": "1.0.0",
            "docs": "/docs"
        }

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
