"""
文本嵌入服务
从 LLM 服务中拆分出来，专注于文本向量化
"""
import os
from typing import List, Optional

import dashscope
from dashscope import TextEmbedding
from langchain.embeddings.base import Embeddings

from app.core.config import settings


class EmbeddingService:
    """文本嵌入服务"""

    def __init__(self):
        api_key = settings.DASHSCOPE_API_KEY or os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY not set")
        dashscope.api_key = api_key
        self.model = settings.EMBEDDING_MODEL

    def embed_text(self, text: str) -> Optional[List[float]]:
        """获取单个文本的 embedding"""
        try:
            resp = TextEmbedding.call(model=self.model, input=text)
            if resp.status_code == 200:
                return resp.output["embeddings"][0]["embedding"]
            else:
                print(f"Embedding error: {resp.message}")
                return None
        except Exception as e:
            print(f"Embedding exception: {e}")
            return None

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量获取文本 embedding"""
        embeddings = []
        for text in texts:
            embedding = self.embed_text(text)
            if embedding:
                embeddings.append(embedding)
            else:
                # 失败时返回零向量
                embeddings.append([0.0] * 1536)
        return embeddings


class DashScopeEmbeddings(Embeddings):
    """LangChain 兼容的 Embedding 适配器"""

    def __init__(self):
        self.service = EmbeddingService()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文档"""
        return self.service.embed_batch(texts)

    def embed_query(self, text: str) -> List[float]:
        """嵌入查询"""
        embedding = self.service.embed_text(text)
        if embedding:
            return embedding
        return [0.0] * 1536
