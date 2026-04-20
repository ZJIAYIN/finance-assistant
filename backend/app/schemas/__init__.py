"""
Pydantic schemas for request/response validation
"""
from .auth import RegisterRequest, LoginRequest, TokenResponse, UserInfo, RefreshRequest
from .session import SessionCreate, SessionUpdate, SessionResponse, MessageResponse, SessionHistoryResponse
from .chat import ChatRequest, ChatResponse
from .crawler import CrawlTestResponse, VectorizeResponse, CrawlStatusResponse

__all__ = [
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "UserInfo",
    "RefreshRequest",
    # Session
    "SessionCreate",
    "SessionUpdate",
    "SessionResponse",
    "MessageResponse",
    "SessionHistoryResponse",
    # Chat
    "ChatRequest",
    "ChatResponse",
    # Crawler
    "CrawlTestResponse",
    "VectorizeResponse",
    "CrawlStatusResponse",
]
