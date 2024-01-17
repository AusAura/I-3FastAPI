from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Tag, Publication, PublicationTagAssociation
from src.schemas.tags import TagBase, TagUpdate
from src.utils.my_logger import logger


async def create_tags(body_tags: list[TagBase], db: AsyncSession):
    tags = []
    for body in body_tags:
        stmt = select(Tag).where(Tag.name == body.name)
        result = await db.execute(stmt)
        tag = result.scalar_one_or_none()

        if tag is None:
            tag = Tag(name=body.name)
            db.add(tag)
            await db.commit()
            await db.refresh(tag)
        tags.append(tag)
        logger.info(f'Tag created: {tag.name}')
    return tags


async def append_tags_to_publication(publication, tags: list[Tag]):
    # Limit to add maximum 5 tags
    if len(publication.tags) + len(tags) > 5:
        raise ValueError("Exceeded the maximum allowed tags for a publication (5).")

    for tag in tags:
        publication.tags.append(tag)
    return publication


async def delete_tags_from_publication(publication, tags: list[Tag], db: AsyncSession):
    for tag in tags:
        if tag in publication.tags:
            publication.tags.remove(tag)
            # TODO: Check if the tag is not associated with any other publications, delete if not
            stmt = select(PublicationTagAssociation).filter_by(tag_id=tag.id)
            result = await db.execute(stmt)
            association_count = result.scalar()
            if association_count == 0:
                await db.delete(tag)
                logger.info(f'Tag deleted: {tag.name}')
    await db.commit()
    return publication

async def get_tag_id_by_name(body, db):
    stmt = select(Tag).where(Tag.name == body.name)
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()
    return tag.id


async def delete_tag_from_publication_by_name(publication_id, body, db):
    tag_id = await get_tag_id_by_name(body, db)
    stmt = select(PublicationTagAssociation).filter_by(tag_id=tag_id, publication_id=publication_id)
    pub_as_tag = await db.execute(stmt)
    pub_as_tag = pub_as_tag.scalar_one_or_none()
    if pub_as_tag is not None:
        await db.delete(pub_as_tag)
        await db.commit()
