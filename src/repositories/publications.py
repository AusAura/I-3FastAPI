from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Publication, PubImage
from src.repositories.tags import create_tags
from src.schemas.publications import PublicationCreate, PubImageSchema, PublicationUpdate
from src.schemas.tags import TagBase
from src.utils.my_logger import logger
from src.schemas.publications import PublicationCreate, PublicationUpdate
from src.schemas.pub_images import BaseImageSchema, PubImageSchema


async def create_pub_img(img_body: PubImageSchema, db: AsyncSession):
    """
    Create new pub_img in database.
    :param img_body: PubImageSchema: pub_img schema to create in database
    :param db: AsyncSession: database session to create pub_img in database
    :return: PubImage: pub_img created in database

    """
    pub_img = PubImage(**img_body.model_dump(exclude_unset=True))
    db.add(pub_img)
    await db.commit()
    await db.refresh(pub_img)
    return pub_img


async def create_publication(body: PublicationCreate, img_body: PubImageSchema, db: AsyncSession, user: User):
    """
    Create new publication in database.
    :param body: PublicationCreate: publication schema to create in database
    :param img_body: PubImageSchema: pub_img schema to create in database
    :param db: AsyncSession: database session to create publication in database
    :param user: User: user to create publication
    :return: Publication: publication created in database

    """
    pub_img = await create_pub_img(img_body, db)
    publication = Publication(**body.model_dump(exclude_unset=True, exclude={'tags'}), user=user, image=pub_img)

    tags = await create_tags(body.tags, db)

    for tag in tags:
        publication.tags.append(tag)

    db.add(publication)
    await db.commit()
    await db.refresh(publication)

    return publication


async def get_user_publications(limit: int, offset: int, db: AsyncSession, user: User):
    """
    Get all user publications from database.
    :param limit: int: limit of publications to get
    :param offset: int: offset of publications to get
    :param db: AsyncSession: database session to get publications from database
    :param user: User: user to get publications
    :return: List[Publication]: list of publications from database

    """
    stmt = (select(Publication).filter_by(user=user)
            .offset(offset).limit(limit)
            .order_by(Publication.created_at.desc()))

    publications = await db.execute(stmt)

    return publications.unique().scalars().all()


async def get_all_publications(limit: int, offset: int, db: AsyncSession):
    """
    Get all publications from database.
    :param limit: int: limit of publications to get
    :param offset: int: offset of publications to get
    :param db: AsyncSession: database session to get publications from database
    :return: List[Publication]: list of publications from database

    """
    stmt = (select(Publication)
            .offset(offset).limit(limit)
            .order_by(Publication.created_at.desc()))

    publications = await db.execute(stmt)

    return publications.unique().scalars().all()


async def get_publication_by_id(publication_id: int, db: AsyncSession, user: User | None = None):
    """
    Get publication by id from database.
    :param publication_id: int: id of publication to get
    :param db: AsyncSession: database session to get publication from database
    :param user: User | None: user to get publication
    :return: Publication | None: publication from database

    """
    if user:
        stmt = select(Publication).filter_by(id=publication_id, user=user)
    else:
        stmt = select(Publication).filter_by(id=publication_id)
    publication = await db.execute(stmt)
    return publication.unique().scalar_one_or_none()


async def update_text_publication(publication_id: int, body: PublicationUpdate, db: AsyncSession, user: User):
    """
    Update text of publication in database.
    :param publication_id: int: id of publication to update in database
    :param body: PublicationUpdate: publication schema to update in database
    :param db: AsyncSession: database session to update publication in database
    :param user: User: user to update publication
    :return: Publication: publication updated in database

    """
    publication = await get_publication_by_id(publication_id, db, user)
    if publication is not None:
        for field, value in body.model_dump(exclude_unset=True).items():
            setattr(publication, field, value)
        await db.commit()
        await db.refresh(publication)

    return publication


async def update_image(publication_id: int, body: BaseImageSchema, db: AsyncSession, user: User):
    """
    Update image of publication in database.
    :param publication_id: int: id of publication to update in database
    :param body: BaseImageSchema: image schema to update in database
    :param db: AsyncSession: database session to update publication in database
    :param user: User: user to update publication
    :return: Publication: publication updated in database

    """
    stmt = select(Publication).filter_by(id=publication_id, user=user)
    publication = await db.execute(stmt)
    publication = publication.unique().scalar_one_or_none()

    if publication is not None:
        for field, value in body.model_dump(exclude_unset=True).items():
            setattr(publication.image, field, value)

        await db.commit()
        await db.refresh(publication)

    return publication


async def delete_publication(publication_id: int, db: AsyncSession, user: User):
    """
    Delete publication from database.
    :param publication_id: int: id of publication to delete from database
    :param db: AsyncSession: database session to delete publication from database
    :param user: User: user to delete publication
    :return: Publication: publication deleted from database

    """
    stmt = select(Publication).filter_by(id=publication_id, user=user)
    publication = await db.execute(stmt)
    publication = publication.unique().scalar_one_or_none()

    if publication is not None:
        await db.delete(publication)
        await db.commit()

    return publication
