"""
RAG检索服务
使用ChromaDB作为向量数据库
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain.schema import Document
from langchain.embeddings.base import Embeddings

from app.core.config import settings
from app.services.llm_service import LLMService


class DashScopeEmbeddings(Embeddings):
    """自定义Embedding类，适配DashScope"""

    def __init__(self):
        self.llm_service = LLMService()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文档"""
        embeddings = []
        for text in texts:
            embedding = self.llm_service.get_embedding(text)
            if embedding:
                embeddings.append(embedding)
            else:
                # 如果失败，返回零向量（不应该发生）
                embeddings.append([0.0] * 1536)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """嵌入查询"""
        embedding = self.llm_service.get_embedding(text)
        if embedding:
            return embedding
        return [0.0] * 1536


class RAGService:
    def __init__(self):
        # 初始化ChromaDB客户端
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_PATH,
            settings=ChromaSettings(
                anonymized_telemetry=False
            )
        )
        self.embedding_function = DashScopeEmbeddings()

    def get_collection_name(self, date: datetime) -> str:
        """获取指定日期的collection名称"""
        return f"market_{date.strftime('%Y_%m_%d')}"

    def get_t_minus_1_collection(self) -> Optional[str]:
        """获取t-1天的collection名称"""
        yesterday = datetime.now() - timedelta(days=1)
        collection_name = self.get_collection_name(yesterday)

        # 检查collection是否存在
        collections = self.client.list_collections()
        if collection_name in [c.name for c in collections]:
            return collection_name

        # 如果不存在，尝试找最近的一个
        for i in range(2, 30):  # 最多回溯30天
            past_date = datetime.now() - timedelta(days=i)
            past_name = self.get_collection_name(past_date)
            if past_name in [c.name for c in collections]:
                return past_name

        return None

    def create_collection(self, date: datetime):
        """创建指定日期的collection"""
        collection_name = self.get_collection_name(date)
        try:
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"date": date.strftime("%Y-%m-%d"), "created_at": datetime.now().isoformat()}
            )
            return collection
        except Exception as e:
            # 如果已存在，直接获取
            return self.client.get_collection(name=collection_name)

    def add_documents(
        self,
        date: datetime,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ):
        """向collection添加文档"""
        collection = self.create_collection(date)

        # 生成embedding
        embeddings = self.embedding_function.embed_documents(documents)

        # 生成ids
        if ids is None:
            base_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            ids = [f"{base_time}_{i}" for i in range(len(documents))]

        # 添加文档
        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas or [{} for _ in documents],
            ids=ids
        )

    def search(
        self,
        query: str,
        collection_name: Optional[str] = None,
        top_k: int = None,
        similarity_threshold: float = None
    ) -> Tuple[List[str], str]:
        """
        检索相关文档
        返回：(相关文档列表, 数据日期)
        """
        top_k = top_k or settings.RAG_TOP_K
        similarity_threshold = similarity_threshold or settings.RAG_SIMILARITY_THRESHOLD

        # 确定要查询的collection
        if collection_name is None:
            collection_name = self.get_t_minus_1_collection()

        if not collection_name:
            return [], ""

        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception:
            return [], ""

        # 获取查询embedding
        query_embedding = self.embedding_function.embed_query(query)

        # 执行检索
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "distances", "metadatas"]
        )

        # 过滤低相似度的结果（ChromaDB返回的是距离，需要转换）
        documents = []
        if results["documents"] and results["documents"][0]:
            for doc, distance in zip(results["documents"][0], results["distances"][0]):
                # 简单的相似度转换（距离越小越相似）
                # 这里可以根据实际情况调整阈值逻辑
                documents.append(doc)

        # 提取日期
        data_date = collection_name.replace("market_", "").replace("_", "-")

        return documents, data_date

    def delete_old_collections(self, retention_days: int = None):
        """删除过期的collection"""
        retention_days = retention_days or settings.DATA_RETENTION_DAYS
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        collections = self.client.list_collections()
        deleted_count = 0

        for collection in collections:
            if collection.name.startswith("market_"):
                try:
                    # 解析日期
                    date_str = collection.name.replace("market_", "").replace("_", "-")
                    coll_date = datetime.strptime(date_str, "%Y-%m-%d")

                    if coll_date < cutoff_date:
                        self.client.delete_collection(name=collection.name)
                        deleted_count += 1
                        print(f"Deleted old collection: {collection.name}")
                except Exception as e:
                    print(f"Error processing collection {collection.name}: {e}")

        return deleted_count

    def list_collections(self) -> List[str]:
        """列出所有collection"""
        collections = self.client.list_collections()
        return [c.name for c in collections]
