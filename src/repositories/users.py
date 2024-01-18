from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.database.models import User, Publication
from src.schemas.user import UserSchema
from src.services.profile import calculate_usage_days
from src.utils.my_logger import logger


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    role = 'admin' if await count_users(db) == 0 else 'user'
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar, role=role)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user


async def count_users(db: AsyncSession) -> int:
    stmt = select(func.count(User.id))
    result = await db.execute(stmt)
    return result.scalar()


async def get_user_by_username(username: str, db: AsyncSession):
    stmt = select(User).filter_by(username=username)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    logger.info(f"{user}")
    return user


async def count_user_publications(user_id: int, db: AsyncSession) -> int:
    stmt = select(func.count(Publication.id)).filter_by(user_id=user_id).select_from(Publication)
    result = await db.execute(stmt)
    return result.scalar()


async def update_username(user: User, new_username: str, db: AsyncSession) -> User:
    user.username = new_username
    await db.commit()
    await db.refresh(user)
    return user



