"""
对话记录 Repository
"""
from typing import List
from sqlalchemy.orm import Session

from app.models import Conversation
from .base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """对话记录数据访问"""

    def __init__(self, db: Session):
        super().__init__(db, Conversation)

    def get_by_session(self, session_id: int, user_id: int) -> List[Conversation]:
        """获取会话的所有消息"""
        return (
            self.db.query(Conversation)
            .filter(
                Conversation.session_id == session_id,
                Conversation.user_id == user_id
            )
            .order_by(Conversation.created_at.asc())
            .all()
        )

    def get_by_session_paginated(
        self, session_id: int, user_id: int, *, skip: int = 0, limit: int = 100
    ) -> List[Conversation]:
        """分页获取会话消息"""
        return (
            self.db.query(Conversation)
            .filter(
                Conversation.session_id == session_id,
                Conversation.user_id == user_id
            )
            .order_by(Conversation.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_session(self, session_id: int) -> int:
        """统计会话消息数量"""
        return (
            self.db.query(Conversation)
            .filter(Conversation.session_id == session_id)
            .count()
        )

    def get_recent_by_session(
        self, session_id: int, user_id: int, limit: int = 20
    ) -> List[Conversation]:
        """获取最近的对话记录（用于上下文）"""
        return (
            self.db.query(Conversation)
            .filter(
                Conversation.session_id == session_id,
                Conversation.user_id == user_id
            )
            .order_by(Conversation.created_at.desc())
            .limit(limit)
            .all()
        )
