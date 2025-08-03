from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from src.database import get_database
from src.models.bookmark_model import Bookmark
from src.schemas.user_schema import CurrentUser
from src.schemas.bookmark_schema import BookmarkCreate, BookmarkResponse
from src.utils.helper import create_unique_short_code, get_current_user

router = APIRouter(prefix="/bookmark", tags=["bookmark"])


@router.post(
    "/create", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED
)
async def handle_post_create(
    bookmark: BookmarkCreate,
    db: AsyncSession = Depends(get_database),
    current_user: CurrentUser = Depends(get_current_user),
):
    existing_bookmark = await db.execute(
        select(Bookmark).filter(Bookmark.original_url == str(bookmark.original_url))
    )

    if existing_bookmark.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Bookmark exists"
        )

    short_code = await create_unique_short_code(db)

    db_bookmark = Bookmark(
        original_url=str(bookmark.original_url),
        short_code=short_code,
        user_id=current_user.id,
    )

    db.add(db_bookmark)
    await db.commit()
    await db.refresh(db_bookmark)

    return db_bookmark


@router.get("/get/all", response_model=List[BookmarkResponse])
async def handle_get_all(
    db: AsyncSession = Depends(get_database),
    current_user: CurrentUser = Depends(get_current_user),
):
    result = await db.execute(
        select(Bookmark).filter(Bookmark.user_id == current_user.id)
    )
    bookmarks = result.scalars().all()
    return bookmarks


@router.get("/get/{bookmark_id}", response_model=BookmarkResponse)
async def handle_get_by_id(
    bookmark_id: str,
    db: AsyncSession = Depends(get_database),
    current_user: CurrentUser = Depends(get_current_user),
):
    result = await db.execute(
        select(Bookmark).filter(
            Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id
        )
    )
    bookmark = result.scalars().first()

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found"
        )

    return bookmark


@router.delete(
    "/delete/{bookmark_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def handle_delete_by_id(
    bookmark_id: str,
    db: AsyncSession = Depends(get_database),
    current_user: CurrentUser = Depends(get_current_user),
):
    result = await db.execute(
        select(Bookmark).filter(
            Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id
        )
    )
    bookmark = result.scalars().first()

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found"
        )

    await db.delete(bookmark)
    await db.commit()

    return None
