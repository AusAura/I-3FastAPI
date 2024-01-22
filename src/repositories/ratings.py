from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Publication, Rating
from src.schemas.ratings import RatingCreate


async def add_rating(publication_id: int, body: RatingCreate, db: AsyncSession, user: User):
    rating = Rating(**body.model_dump(exclude_unset=True), user=user, publication_id=publication_id)
    db.add(rating)
    await db.commit()
    await db.refresh(rating)
    return rating


async def get_all_ratings_by_user_id(user_id: int, db: AsyncSession, limit: int, offset: int):
    stmt = select(Rating).filter_by(user_id=user_id).limit(limit).offset(offset)
    ratings = await db.execute(stmt)
    return ratings.unique().scalars().all()


async def get_users_by_ratings(ratings: list[Rating], db: AsyncSession, limit: int, offset: int):
    stmt = (select(User).filter(User.id.in_([rating.user_id for rating in ratings]))
            .limit(limit).offset(offset))
    users = await db.execute(stmt)
    return users.scalars().all()
