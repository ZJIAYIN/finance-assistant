"""
对话相关 schemas
"""
from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: int
    message: str


class ChatResponse(BaseModel):
    answer: str
    data_date: str
    retrieved_count: int
