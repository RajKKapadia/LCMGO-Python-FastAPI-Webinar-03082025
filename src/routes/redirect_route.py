from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database import get_database
from src.models.bookmark_model import Bookmark

router = APIRouter(prefix="/redirect", tags=["redirects"])


@router.get("/code/{short_code}")
async def handle_get_short_code(
    short_code: str, db: AsyncSession = Depends(get_database)
):
    result = await db.execute(
        select(Bookmark).filter(Bookmark.short_code == short_code)
    )
    bookmark = result.scalars().first()

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found"
        )

    bookmark.visit_count += 1
    await db.commit()

    return RedirectResponse(url=bookmark.original_url)
