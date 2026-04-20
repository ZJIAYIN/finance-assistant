"""
会话管理接口
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas import (
    SessionCreate, SessionUpdate, SessionResponse,
    SessionHistoryResponse, MessageResponse
)
from app.api.deps import get_db, get_current_user_id, get_session_repo, get_conversation_repo
from app.repositories import SessionRepository, ConversationRepository

router = APIRouter()


@router.get("", response_model=List[SessionResponse])
def list_sessions(
    user_id: int = Depends(get_current_user_id),
    session_repo: SessionRepository = Depends(get_session_repo),
    conversation_repo: ConversationRepository = Depends(get_conversation_repo)
):
    """获取用户的所有会话列表"""
    sessions = session_repo.get_by_user(user_id)

    result = []
    for session in sessions:
        msg_count = conversation_repo.count_by_session(session.id)

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
    from app.models import ChatSession

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
    session_repo: SessionRepository = Depends(get_session_repo),
    conversation_repo: ConversationRepository = Depends(get_conversation_repo)
):
    """获取会话历史消息"""
    session = session_repo.get_by_user_and_id(user_id, session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )

    messages = conversation_repo.get_by_session(session_id, user_id)
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
    session_repo: SessionRepository = Depends(get_session_repo),
    conversation_repo: ConversationRepository = Depends(get_conversation_repo)
):
    """更新会话名称"""
    session = session_repo.get_by_user_and_id(user_id, session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )

    session.session_name = request.session_name
    session_repo.db.commit()
    session_repo.db.refresh(session)

    msg_count = conversation_repo.count_by_session(session.id)

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
    session_repo: SessionRepository = Depends(get_session_repo)
):
    """删除会话及其所有对话记录"""
    session = session_repo.get_by_user_and_id(user_id, session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )

    session_repo.delete(session_id)

    return {"message": "会话已删除"}
