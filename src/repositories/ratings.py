from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Publication, Rating
from src.schemas.ratings import RatingCreate


async def add_rating(publication_id: int, body: RatingCreate, db: AsyncSession, user: User):
    rating = Rating(**body.model_dump(exclude_unset=True), user=user, publication_id=publication_id)
    db.add(rating)
    await db.commit()
    await db.refresh(rating)
    return rating

