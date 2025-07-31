from sqlalchemy import String, Boolean
from sqlalchemy.orm import mapped_column, Mapped
from .base import Base

class User(Base):
    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self):
        return f'User(id: {self.id}, username: {self.username})'