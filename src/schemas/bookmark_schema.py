from datetime import datetime

from pydantic import BaseModel


class BookmarkCreate(BaseModel):
    original_url: str


class BookmarkResponse(BaseModel):
    id: str
    original_url: str
    short_code: str
    visit_count: int
    created_at: datetime
    user_id: str
