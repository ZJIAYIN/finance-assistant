"""
金融投资智能助手 - FastAPI后端入口
"""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db
from app.core.exceptions import AppException
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
    app.include_router(api_router)

    # 全局异常处理器
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message}
        )

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

    @app.get("/")
    def root():
        return {
            "message": "金融投资智能助手API服务",
            "version": "1.0.0",
            "docs": "/docs"
        }

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
