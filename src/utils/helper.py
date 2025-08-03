import json
from datetime import datetime, timezone
import random
import string

from passlib.context import CryptContext
from fastapi.requests import Request
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_database
from src.schemas.user_schema import CurrentUser, SessionData
from src import config
from src.models.user_model import User
from src.models.bookmark_model import Bookmark

pwd_context = CryptContext(schemes=["sha256_crypt"])


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_database)
) -> CurrentUser:
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    session_id = auth_header.split(" ", maxsplit=1)[1]

    try:
        session_data = config.redis_client.get(session_id)
        if session_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No session found",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error while fetching session data",
            headers={"WWW-Authenticate": "Bearer"},
        )

    session_data = SessionData(**json.loads(session_data))

    now_at = datetime.now(tz=timezone.utc).timestamp()
    time_difference_seconds = now_at - session_data.last_used_at
    time_difference_minutes = time_difference_seconds / 60

    if time_difference_minutes > config.SESSION_EXPIRATION_TIME:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    session_data.last_used_at = now_at
    config.redis_client.set(session_id, session_data.model_dump_json())

    result = await db.execute(select(User).filter(User.id == session_data.user_id))
    db_user = result.scalars().first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    current_user = CurrentUser(
        id=db_user.id,
        email=db_user.email,
        hashed_password=db_user.hashed_password,
        session_id=session_id,
    )
    return current_user


def generate_short_code(length: int = 16):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


async def create_unique_short_code(db: AsyncSession):
    while True:
        short_code = generate_short_code()
        result = await db.execute(
            select(Bookmark).filter(Bookmark.short_code == short_code)
        )
        exists = result.scalars().first()
        if not exists:
            return short_code
