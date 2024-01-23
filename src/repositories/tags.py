from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.database.models import Tag, Publication, PublicationTagAssociation, User
from src.schemas.tags import TagSchema, TagUpdate
from src.repositories import publications as repositories_publications
from src.utils.my_logger import logger


async def create_tag(tag: TagSchema, db: AsyncSession) -> Tag:
    new_tag = Tag(**tag.model_dump(exclude_unset=True))
    db.add(new_tag)
    try:
        await db.commit()
        await db.refresh(new_tag)
    except IntegrityError as e:
        pass
    return new_tag


async def create_tags(tags: list[TagSchema], db: AsyncSession) -> list[Tag]:

    return [await create_tag(tag, db) for tag in tags]

