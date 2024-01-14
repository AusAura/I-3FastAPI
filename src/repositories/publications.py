from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Publication, PubImage
from src.schemas.publications import PublicationCreate, PubImageSchema
from src.utils.my_logger import logger


async def create_pub_img(img_body: PubImageSchema, db: AsyncSession):
    pub_img = PubImage(**img_body.model_dump(exclude_unset=True))
    db.add(pub_img)
    await db.commit()
    await db.refresh(pub_img)
    return pub_img


async def create_publication(body: PublicationCreate, img_body: PubImageSchema, db: AsyncSession, user: User):
    pub_img = await create_pub_img(img_body, db)
    publication = Publication(**body.model_dump(exclude_unset=True), user=user, image=pub_img)
    db.add(publication)
    await db.commit()
    await db.refresh(publication)

    return publication


async def get_publications(limit, offset, db, user):

    stmt = select(Publication).filter_by(user=user).offset(offset).limit(limit)
    publications = await db.execute(stmt)
    return publications.scalars().all()

