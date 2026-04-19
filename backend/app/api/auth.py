"""
认证相关接口
"""
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id, decode_token
from app.services.auth_service import AuthService

router = APIRouter()


# 请求/响应模型
class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserInfo(BaseModel):
    id: int
    username: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register", response_model=UserInfo)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    auth_service = AuthService(db)

    if len(request.username) < 3 or len(request.username) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名长度必须在3-20个字符之间"
        )

    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度至少6个字符"
        )

    user = auth_service.register(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    return UserInfo(id=user.id, username=user.username)


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    auth_service = AuthService(db)
    user = auth_service.authenticate(request.username, request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, refresh_token = auth_service.create_tokens(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=60 * 24  # 24小时，分钟
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: RefreshRequest):
    """刷新访问令牌"""
    payload = decode_token(request.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )

    # 创建新的token
    auth_service = AuthService(None)  # 不需要db
    access_token, refresh_token = auth_service.create_tokens(int(user_id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=60 * 24
    )


@router.get("/me", response_model=UserInfo)
def get_me(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """获取当前用户信息"""
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return UserInfo(id=user.id, username=user.username)
