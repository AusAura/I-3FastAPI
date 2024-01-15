from sqlalchemy import select, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tag, Publication

from src.schemas.tags import TagCreate, TagUpdate, TagBase
from typing import List, Sequence

from src.utils.my_logger import logger


async def add_tag(body_tag: TagBase, db: AsyncSession) -> Tag:
    """
    Add a new tag.
    """
    tag = Tag(name=body_tag.name)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def add_tags_to_publication(tags: list[TagBase], publication, db: AsyncSession):
    """
    Add tags to new publication.
    """
    tags: list[Tag] = [await add_tag(tag, db) for tag in tags]
    logger.debug(f'Add tags: {tags} to publication: {publication}')

    publication.tags.extend(tags)

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
