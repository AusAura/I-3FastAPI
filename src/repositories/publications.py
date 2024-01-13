from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Publication, PubImage
from src.schemas.publications import PublicationCreate, PubImageSchema


async def create_publication(body: PublicationCreate, img_body: PubImageSchema, db: AsyncSession, user: User):
    publication = Publication(**body.model_dump(exclude_unset=True))
    # publication.image = PubImage(**img_body.model_dump(exclude_unset=True))
    if user is not None:
        publication.user_id = user.id

    db.add(publication)
    await db.commit()
    await db.refresh(publication)
    return publication
