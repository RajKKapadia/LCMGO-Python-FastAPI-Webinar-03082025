from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src import config
from src import logging

logger = logging.getLogger(__name__)

async_engine = create_async_engine(url=config.DATABASE_URL)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_database():
    logger.info("Creating a new database session...")
    try:
        async with AsyncSessionLocal() as async_session:
            yield async_session
            logger.info("Database session closed...")
    except Exception as e:
        logger.error(f"Unable to create database session: {str(e)}")
        raise
