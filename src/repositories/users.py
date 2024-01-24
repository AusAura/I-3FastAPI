from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.database.models import User, Publication
from src.schemas.user import UserSchema

from src.utils.my_logger import logger


async def get_user_by_email(email: str, db: AsyncSession):
    """
    Get user by email from db table User

    :param email: str: user email from request body
    :param db: AsyncSession: database connection
    :return: user object: user object from db

    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


# admin
async def get_user_by_publication_id(publication_id: int, db: AsyncSession):
    """
    Get user by publication_id from db table Publication

    :param publication_id: int: publication id from request body
    :param db: AsyncSession: database connection
    :return: user object: user object from db

    """
    pub = await db.execute(select(Publication).filter_by(id=publication_id))
    pub = pub.scalar_one_or_none()
    user = pub.user
    return user


# admin
async def get_user_by_id(user_id: int, db: AsyncSession):
    """
    Get user by id from db table User

    :param user_id: int: user id from request body
    :param db: AsyncSession: database connection
    :return: user object: user object from db

    """
    user = await db.execute(select(User).filter_by(id=user_id))
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession):
    """
    Create new user in db table User

    :param body: UserSchema: user object from request body
    :param db: AsyncSession: database connection
    :return: user object: user object from db

    """
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
    """
    Update user token in db table User

    :param user: User: user object from db
    :param token: str | None: user token from request body
    :param db: AsyncSession: database connection
    :return: user object: user object from db

    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    Update user confirmed in db table User

    :param email: str: user email from request body
    :param db: AsyncSession: database connection
    :return: None

    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def count_users(db: AsyncSession) -> int:
    """
    Count users in db table User

    :param db: AsyncSession: database connection
    :return: int: count of users

    """
    stmt = select(func.count(User.id))
    result = await db.execute(stmt)
    return result.scalar()
