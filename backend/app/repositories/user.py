"""
用户 Repository
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.models import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """用户数据访问"""

    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_username(self, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()

    def exists(self, username: str) -> bool:
        """检查用户名是否存在"""
        return self.db.query(User).filter(User.username == username).first() is not None
