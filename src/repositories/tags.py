from sqlalchemy import select, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tag, Publication, PublicationTagAssociation

from src.schemas.tags import TagBase, TagUpdate
from typing import Sequence

from src.utils.my_logger import logger


async def create_tags(body_tags: list[TagBase], db: AsyncSession):
    tags = []
    for body in body_tags:
        # Check if the tag already exists
        stmt = select(Tag).where(Tag.name == body.name)
        result = await db.execute(stmt)
        tag = result.scalar_one_or_none()

        if tag is None:
            # If the tag doesn't exist, create it
            tag = Tag(name=body.name)
            db.add(tag)
            await db.commit()
            await db.refresh(tag)
        tags.append(tag)
        logger.info(f'tag created: {tag}')
    return tags


async def create_publication_tag_association(publication: Publication, tags: list[Tag], db: AsyncSession):
    for tag in tags:
        await db.refresh(tag)
        await db.refresh(publication)
        publication_tag = PublicationTagAssociation(publication_id=publication.id, tag_id=tag.id)
        db.add(publication_tag)
        await db.commit() # TODO что то с этим делать
    await db.refresh(publication)
    return publication








async def delete_tag(tag_id: int, db: AsyncSession) -> None:
    """
    Delete a tag by ID.
    """
    stmt = delete(Tag).where(Tag.id == tag_id)
    await db.execute(stmt)
    await db.commit()


async def get_tag(tag_id: int, db: AsyncSession) -> Tag | None:
    """
    Get a tag by ID.
    """
    stmt = select(Tag).filter_by(id=tag_id)
    tag = await db.execute(stmt)
    return tag.scalar_one_or_none()


async def get_tags(db: AsyncSession) -> Sequence[Tag]:
    """
    Get all tags.
    """
    stmt = select(Tag)
    tags = await db.execute(stmt)
    return tags.scalars().all()


async def edit_tag(tag_id: int, tag_update: TagUpdate, db: AsyncSession) -> Tag | None:
    """
    Edit a tag by ID.
    """
    stmt = update(Tag).where(Tag.id == tag_id).values(tag_update.dict(exclude_unset=True))
    await db.execute(stmt)
    await db.commit()
    return await get_tag(tag_id, db)
