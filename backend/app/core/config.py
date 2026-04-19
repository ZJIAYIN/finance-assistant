"""
项目配置
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "金融投资智能助手"
    DEBUG: bool = True

    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./db/app.db"

    # ChromaDB配置
    CHROMA_DB_PATH: str = "./data/chroma"

    # DashScope配置
    DASHSCOPE_API_KEY: str = ""  # 用户需要填入自己的key
    EMBEDDING_MODEL: str = "text-embedding-v2"
    LLM_MODEL: str = "qwen-max"  # 或 qwen-turbo

    # 数据保留配置
    DATA_RETENTION_DAYS: int = 7  # 向量数据保留天数

    # RAG配置
    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.7
    MAX_HISTORY_MESSAGES: int = 20  # 历史消息数量限制

    # 爬虫配置
    CRAWL_TIME: str = "09:00"  # 每日更新时间
    DATA_SOURCE_URL: str = "https://quote.eastmoney.com/"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
