"""
API 依赖注入
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_token
from app.core.exceptions import AuthenticationError
from app.repositories import UserRepository, SessionRepository, ConversationRepository
from app.services.auth_service import AuthService
from app.services.agent_service import AgentService

security_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Repository dependencies
def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_session_repo(db: Session = Depends(get_db)) -> SessionRepository:
    return SessionRepository(db)


def get_conversation_repo(db: Session = Depends(get_db)) -> ConversationRepository:
    return ConversationRepository(db)


# Service dependencies
def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo)
) -> AuthService:
    return AuthService(user_repo)


def get_agent_service(
    db: Session = Depends(get_db),
    conversation_repo: ConversationRepository = Depends(get_conversation_repo)
) -> AgentService:
    return AgentService(db, conversation_repo)


# Authentication dependencies
async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> int:
    """获取当前用户ID（依赖注入用）"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub")
    token_type: str = payload.get("type")

    if user_id is None or token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return int(user_id)


async def get_current_user_id_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> Optional[int]:
    """可选的用户认证"""
    if not credentials:
        return None

    payload = decode_token(credentials.credentials)
    if not payload:
        return None

    user_id = payload.get("sub")
    token_type = payload.get("type")

    if user_id is None or token_type != "access":
        return None

    return int(user_id)
