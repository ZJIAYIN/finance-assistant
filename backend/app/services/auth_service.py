"""
用户认证服务
"""
from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models import User
from app.core.security import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token
)


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, username: str, password: str) -> Optional[User]:
        """用户注册"""
        # 检查用户名是否已存在
        existing_user = self.db.query(User).filter(User.username == username).first()
        if existing_user:
            return None

        # 创建新用户
        password_hash = get_password_hash(password)
        user = User(username=username, password_hash=password_hash)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """用户认证"""
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None

        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        self.db.commit()
        return user

    def create_tokens(self, user_id: int) -> Tuple[str, str]:
        """创建访问令牌和刷新令牌"""
        access_token = create_access_token(data={"sub": str(user_id)})
        refresh_token = create_refresh_token(data={"sub": str(user_id)})
        return access_token, refresh_token

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """通过ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
