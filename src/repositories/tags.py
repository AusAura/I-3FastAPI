from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tag, Publication
from src.schemas.tags import TagCreate, PublicationTagCreate
from typing import List


async def create_or_get_tags(tag_names: List[str], db: AsyncSession) -> List[Tag]:
    """
    Create new tags if they don't exist, or retrieve existing tags by name.
    """
    tags = []
    for tag_name in tag_names:
        tag = await get_tag_by_name(tag_name, db)
        if tag is None:
            # Tag doesn't exist, create a new one
            tag = await create_tag(TagCreate(name=tag_name), db)
        tags.append(tag)
    return tags


async def get_tag_by_name(tag_name: str, db: AsyncSession) -> Tag | None:
    """
    Retrieve a tag by name.
    """
    stmt = select(Tag).filter_by(name=tag_name)
    tag = await db.execute(stmt)
    return tag.scalar_one_or_none()


async def create_tag(tag: TagCreate, db: AsyncSession) -> Tag:
    """
    Create a new tag.
    """
    tag_db = Tag(name=tag.name)  # TODO
    db.add(tag_db)
    await db.commit()
    await db.refresh(tag_db)
    return tag_db


async def add_tags_to_photo(publication_id: int, tags: List[PublicationTagCreate], db: AsyncSession) -> List[Tag]:
    """
    Associate tags with a photo.
    """
    publication = await get_publication_by_id(publication_id, db)
    if not publication:
        return []

    tag_objects = await create_or_get_tags([tag.name for tag in tags], db)

    publication.tags.extend(tag_objects)
    await db.commit()
    await db.refresh(publication)

    return publication.tags


async def get_publication_by_id(publication_id: int, db: AsyncSession) -> Publication | None:
    """
    Retrieve a publication by ID.
    """
    stmt = select(Publication).filter_by(id=publication_id)
    publication = await db.execute(stmt)
    return publication.scalar_one_or_none()
