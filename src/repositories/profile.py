from datetime import datetime

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.models import User, Publication
from src.repositories.users import get_user_by_email
from src.schemas.user import UserNameSchema, AboutSchema

from src.utils.my_logger import logger


async def get_user_by_username(username: str, db: AsyncSession):
    """
    Getting user by username.

    :param username: str: username
    :param db: AsyncSession: database session
    :return: User: user by username

    """
    stmt = select(User).filter_by(username=username)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    logger.info(f"{user}")
    return user


async def count_user_publications(user_id: int, db: AsyncSession) -> int:
    """
    Count user publications.

    :param user_id: int: user id
    :param db: AsyncSession: database session
    :return: int: count user publications

    """
    stmt = select(func.count(Publication.id)).filter_by(user_id=user_id).select_from(Publication)
    result = await db.execute(stmt)
    return result.scalar()


async def update_username(user: User, body: UserNameSchema, db: AsyncSession) -> User:
    """
    Update username.

    :param user: User: user to update username
    :param body: UserNameSchema: username schema to update user
    :param db: AsyncSession: database session to update user in database
    :return: User: updated user

    """
    user.username = body.username
    await db.commit()
    await db.refresh(user)
    return user


async def update_about(user: User, body: AboutSchema, db: AsyncSession) -> User:
    """
    Update about.

    :param user: User: user to update about
    :param body: AboutSchema: about schema to update user
    :param db: AsyncSession: database session to update user in database
    :return: User: updated user

    """
    user.about = body.about
    await db.commit()
    await db.refresh(user)
    return user


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
    Update avatar url.

    :param email: str: email to update avatar url
    :param url: str: url to update avatar
    :param db: AsyncSession: database session to update user in database
    :return: User: updated user

    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user


async def count_usage_days(created_at: datetime, db: AsyncSession) -> int:
    """
    Count usage days.

    :param created_at: datetime: created at time to count usage days
    :param db: AsyncSession: database session to count usage days
    :return: int: count usage days

    """

    now = datetime.now()
    delta = now.day - created_at.day
    logger.info(f"calculate_DELTA________ {delta}")
    return delta
