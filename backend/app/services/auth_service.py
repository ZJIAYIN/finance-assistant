"""
用户认证服务
"""
from datetime import datetime
from typing import Optional, Tuple

from app.models import User
from app.repositories import UserRepository
from app.core.security import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token
)


class AuthService:
    """用户认证服务"""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register(self, username: str, password: str) -> Optional[User]:
        """用户注册"""
        # 检查用户名是否已存在
        if self.user_repo.exists(username):
            return None

        # 创建新用户
        password_hash = get_password_hash(password)
        user = self.user_repo.create({
            "username": username,
            "password_hash": password_hash
        })
        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """用户认证"""
        user = self.user_repo.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None

        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        self.user_repo.db.commit()
        return user

    def create_tokens(self, user_id: int) -> Tuple[str, str]:
        """创建访问令牌和刷新令牌"""
        access_token = create_access_token(data={"sub": str(user_id)})
        refresh_token = create_refresh_token(data={"sub": str(user_id)})
        return access_token, refresh_token

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """通过ID获取用户"""
        return self.user_repo.get(user_id)
