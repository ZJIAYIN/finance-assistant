"""
会话相关 schemas
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


class SessionCreate(BaseModel):
    session_name: Optional[str] = None


class SessionUpdate(BaseModel):
    session_name: str


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_name: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_msg: str
    assistant_msg: str
    data_date: Optional[str] = None
    created_at: datetime


class SessionHistoryResponse(BaseModel):
    session: SessionResponse
    messages: List[MessageResponse]
