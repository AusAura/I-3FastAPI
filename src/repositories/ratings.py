from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Publication, Rating
from src.schemas.ratings import RatingCreate


async def add_rating(publication_id: int, body: RatingCreate, db: AsyncSession, user: User):
    """
    (User) Add rating. If publication already rated, update rating. If not rated, create new rating.
    :param publication_id: id of publication to rate.
    :param body: rating data: user_id, publication_id, rating.
    :param db: database session.
    :param user: current user.
    :return: created rating.

    """
    rating = Rating(**body.model_dump(exclude_unset=True), user=user, publication_id=publication_id)
    db.add(rating)
    await db.commit()
    await db.refresh(rating)
    return rating


async def get_all_ratings_by_user_id(user_id: int, db: AsyncSession, limit: int, offset: int):
    """
    (Admin, Moderator only) Get all ratings by user id.
    :param user_id: user id.
    :param db: database session.
    :param limit: limit of ratings.
    :param offset: offset of ratings.
    :return: list of ratings.

    """
    stmt = select(Rating).filter_by(user_id=user_id).limit(limit).offset(offset)
    ratings = await db.execute(stmt)
    return ratings.unique().scalars().all()


async def get_users_by_ratings(ratings: list[Rating], db: AsyncSession, limit: int, offset: int):
    """
    (Admin, Moderator only) Get users by ratings.
    :param ratings: list of ratings.
    :param db: database session.
    :param limit: limit of users.
    :param offset: offset of users.
    :return: list of users.

    """
    stmt = (select(User).filter(User.id.in_([rating.user_id for rating in ratings]))
            .limit(limit).offset(offset))
    users = await db.execute(stmt)
    return users.scalars().all()


async def delete_rating(user_id, publication_id, db):
    """
    (Admin, Moderator only) Delete rating.
    :param user_id: user id.
    :param publication_id: publication id.
    :param db: database session.
    :return: deleted rating.

    """
    stmt = select(Rating).filter_by(user_id=user_id, publication_id=publication_id)
    rating = await db.execute(stmt)
    rating = rating.unique().scalar_one_or_none()

    if rating is not None:
        await db.delete(rating)
        await db.commit()

    return rating
