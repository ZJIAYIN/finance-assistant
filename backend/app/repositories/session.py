"""
会话 Repository
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models import ChatSession
from .base import BaseRepository


class SessionRepository(BaseRepository[ChatSession]):
    """会话数据访问"""

    def __init__(self, db: Session):
        super().__init__(db, ChatSession)

    def get_by_user(self, user_id: int, *, skip: int = 0, limit: int = 100) -> List[ChatSession]:
        """获取用户的所有会话"""
        return (
            self.db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(desc(ChatSession.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_user_and_id(self, user_id: int, session_id: int) -> Optional[ChatSession]:
        """获取用户的指定会话"""
        return (
            self.db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
            .first()
        )
