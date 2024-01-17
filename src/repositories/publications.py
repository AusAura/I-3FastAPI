from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Publication, PubImage
from src.schemas.publications import PublicationCreate, PubImageSchema, PublicationUpdate, BaseImageSchema, \
    QrCodeImageSchema
from src.utils.my_logger import logger


async def create_pub_img(img_body: PubImageSchema, db: AsyncSession):
    # TODO unique или что-то в єтом вроде что би в папке темп под 1 постом била только 1 картинка
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


async def get_publications(limit: int, offset: int, db: AsyncSession, user: User):
    stmt = (select(Publication).filter_by(user=user)
            .offset(offset).limit(limit)
            .order_by(Publication.created_at.desc()))

    publications = await db.execute(stmt)

    return publications.scalars().all()


async def get_all_publications(limit: int, offset: int, db: AsyncSession):
    stmt = (select(Publication)
            .offset(offset).limit(limit)
            .order_by(Publication.created_at.desc()))

    publications = await db.execute(stmt)

    return publications.scalars().all()


async def get_publication(publication_id: int, db: AsyncSession, user: User):
    stmt = select(Publication).filter_by(id=publication_id, user=user)
    publication = await db.execute(stmt)

    return publication.scalar_one_or_none()


async def update_text_publication(publication_id: int, body: PublicationUpdate, db: AsyncSession, user: User):
    publication = await get_publication(publication_id, db, user)
    if publication is not None:
        for field, value in body.model_dump(exclude_unset=True).items():
            setattr(publication, field, value)
        await db.commit()
        await db.refresh(publication)

    return publication


async def update_image(publication_id: int, body: BaseImageSchema, db: AsyncSession, user: User):

    stmt = select(Publication).filter_by(id=publication_id, user=user)
    publication = await db.execute(stmt)
    publication = publication.scalar_one_or_none()

    if publication is not None:
        for field, value in body.model_dump(exclude_unset=True).items():
            setattr(publication.image, field, value)

        await db.commit()
        await db.refresh(publication)

    return publication


async def delete_publication(publication_id: int, db: AsyncSession, user: User):
    stmt = select(Publication).filter_by(id=publication_id, user=user)
    publication = await db.execute(stmt)
    publication = publication.scalar_one_or_none()

    if publication is not None:
        await db.delete(publication)
        await db.commit()

    return publication
