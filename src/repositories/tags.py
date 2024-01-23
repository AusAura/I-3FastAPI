from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.database.models import Tag, Publication, PublicationTagAssociation, User
from src.schemas.tags import TagSchema
from src.repositories import publications as repositories_publications
from src.utils.my_logger import logger


async def create_tag(tag: TagSchema, db: AsyncSession) -> Tag:
    new_tag = Tag(**tag.model_dump(exclude_unset=True))
    db.add(new_tag)
    try:
        await db.commit()
        await db.refresh(new_tag)
    except IntegrityError as e:
        await db.rollback()
    return new_tag


async def create_tags(tags: list[TagSchema], db: AsyncSession) -> list[Tag]:
    return [await create_tag(tag, db) for tag in tags]


async def get_tag_by_name(body: TagSchema, db: AsyncSession):
    stmt = select(Tag).filter_by(name=body.name)
    tag = await db.execute(stmt)
    tag = tag.unique().scalar_one_or_none()
    return tag


async def publication_extend_tag(publication_id: int, body: TagSchema, db: AsyncSession):
    tag = await get_tag_by_name(body, db)

    stmt = PublicationTagAssociation(publication_id=publication_id, tag_id=tag.id)
    try:
        db.add(stmt)
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
    await db.refresh(tag)
    return tag


async def delete_tag_from_publication(publication_id: int, body: TagSchema, db: AsyncSession):
    tag = await get_tag_by_name(body, db)
    stmt = select(PublicationTagAssociation).filter_by(publication_id=publication_id, tag_id=tag.id)
    association = await db.execute(stmt)
    association = association.unique().scalar_one_or_none()
    if association:
        await db.delete(association)
        await db.commit()
    return association

