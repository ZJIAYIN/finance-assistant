"""
对话记录模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    user_msg = Column(Text, nullable=False)
    assistant_msg = Column(Text, nullable=False)
    data_date = Column(String(10), nullable=True)  # 使用的行情数据日期，如 "2024-04-17"
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="conversations")
    session = relationship("ChatSession", back_populates="conversations")

    def __repr__(self):
        return f"<Conversation {self.id}>"

    def to_message_format(self):
        """转换为LLM message格式"""
        return [
            {"role": "user", "content": self.user_msg},
            {"role": "assistant", "content": self.assistant_msg}
        ]
