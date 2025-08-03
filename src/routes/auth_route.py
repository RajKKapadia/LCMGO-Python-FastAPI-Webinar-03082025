import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_database
from src.models.user_model import User
from src.utils.helper import hash_password, verify_password
from src.schemas.user_schema import AuthUser, NewUser, SessionData, SessionResponse
from src import config

router = APIRouter(prefix="/auth")


@router.post("/register")
async def handle_post_register(
    user: AuthUser, db: AsyncSession = Depends(get_database)
):
    # Check if email already exists
    result = await db.execute(select(User).filter(User.email == user.email))
    db_user_by_username = result.scalars().first()
    if db_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Validate password provider
    if not user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required",
        )

    hashed_password = hash_password(password=user.password)

    new_user = NewUser(email=user.email, hashed_password=hashed_password)

    db_user = User(**new_user.model_dump())

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    session_id = secrets.token_urlsafe(128)

    last_used_at = (datetime.now(tz=timezone.utc)).timestamp()

    session_data = SessionData(user_id=db_user.id, last_used_at=last_used_at)

    config.redis_client.set(
        name=session_id,
        value=session_data.model_dump_json(),
    )

    return SessionResponse(session_id=session_id)


@router.post("/login", response_model=SessionResponse)
async def handle_post_login(
    user: AuthUser,
    db: AsyncSession = Depends(get_database),
):
    # Authenticat user
    result = await db.execute(select(User).filter(User.email == user.email))
    db_user = result.scalars().first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username not found",
        )

    if not verify_password(
        plain_password=user.password, hashed_password=db_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    session_id = secrets.token_urlsafe(128)

    last_used_at = (datetime.now(tz=timezone.utc)).timestamp()

    session_data = SessionData(user_id=db_user.id, last_used_at=last_used_at)

    config.redis_client.set(
        name=session_id,
        value=session_data.model_dump_json(),
    )

    return SessionResponse(session_id=session_id)


# @router.get("/logout", response_model=None, status_code=204)
# async def handle_get_user(
#     current_user: CurrentUser = Depends(get_current_user),
# ):
#     config.redis_client.delete(current_user.session_id)
#     return None