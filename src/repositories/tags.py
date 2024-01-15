from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tag

from src.schemas.tags import TagCreate, TagUpdate
from typing import List


async def add_tag(tag: TagCreate, db: AsyncSession) -> Tag:
    """
    Add a new tag.
    """
    tag_db = Tag(name=tag.name)
    db.add(tag_db)
    await db.commit()
    await db.refresh(tag_db)
    return tag_db


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


async def get_tags(db: AsyncSession) -> List[Tag]:
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


