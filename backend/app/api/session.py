"""
会话管理接口
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models import ChatSession, Conversation

router = APIRouter()


# 请求/响应模型
class SessionCreate(BaseModel):
    session_name: Optional[str] = None


class SessionUpdate(BaseModel):
    session_name: str


class SessionResponse(BaseModel):
    id: int
    session_name: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    user_msg: str
    assistant_msg: str
    data_date: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SessionHistoryResponse(BaseModel):
    session: SessionResponse
    messages: List[MessageResponse]


@router.get("", response_model=List[SessionResponse])
def list_sessions(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取用户的所有会话列表"""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == user_id
    ).order_by(ChatSession.updated_at.desc()).all()

    result = []
    for session in sessions:
        msg_count = db.query(Conversation).filter(
            Conversation.session_id == session.id
        ).count()

        result.append(SessionResponse(
            id=session.id,
            session_name=session.session_name,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=msg_count
        ))

    return result


@router.post("", response_model=SessionResponse)
def create_session(
    request: SessionCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """创建新会话"""
    session_name = request.session_name or "新会话"

    session = ChatSession(
        user_id=user_id,
        session_name=session_name
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return SessionResponse(
        id=session.id,
        session_name=session.session_name,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=0
    )


@router.get("/{session_id}/history", response_model=SessionHistoryResponse)
def get_session_history(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取会话历史消息"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )

    messages = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).order_by(Conversation.created_at.asc()).all()

    msg_count = len(messages)

    return SessionHistoryResponse(
        session=SessionResponse(
            id=session.id,
            session_name=session.session_name,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=msg_count
        ),
        messages=[MessageResponse(
            id=m.id,
            user_msg=m.user_msg,
            assistant_msg=m.assistant_msg,
            data_date=m.data_date,
            created_at=m.created_at
        ) for m in messages]
    )


@router.put("/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: int,
    request: SessionUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """更新会话名称"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )

    session.session_name = request.session_name
    db.commit()
    db.refresh(session)

    msg_count = db.query(Conversation).filter(
        Conversation.session_id == session.id
    ).count()

    return SessionResponse(
        id=session.id,
        session_name=session.session_name,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=msg_count
    )


@router.delete("/{session_id}")
def delete_session(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """删除会话及其所有对话记录"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )

    db.delete(session)
    db.commit()

    return {"message": "会话已删除"}
