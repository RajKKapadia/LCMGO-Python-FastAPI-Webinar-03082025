from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase

from src.models.user_model import User
from src.config import generate_uuid


class BookmarkBase(DeclarativeBase):
    pass


class Bookmark(BookmarkBase):
    __tablename__ = "bookmarks"

    id = Column(String(512), primary_key=True, default=generate_uuid)
    original_url = Column(Text)
    short_code = Column(String(32), unique=True, index=True)
    visit_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(String(512), ForeignKey(User.id))
