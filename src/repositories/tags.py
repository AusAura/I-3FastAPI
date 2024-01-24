from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.database.models import Tag, Publication, PublicationTagAssociation, User
from src.schemas.tags import TagSchema
from src.repositories import publications as repositories_publications
from src.utils.my_logger import logger



# async def create_tags(body_tags: list[TagBase], db: AsyncSession):
#     tags = []
#     for body in body_tags:
#         stmt = select(Tag).where(Tag.name == body.name)
#         result = await db.execute(stmt)
#         tag = result.unique().scalar_one_or_none()

#         if tag is None:
#             tag = Tag(name=body.name)
#             db.add(tag)
#             await db.commit()
#             await db.refresh(tag)
#         tags.append(tag)
#         logger.info(f'Tag created: {tag.name}')
#     return tags


# async def tags_to_publication_by_id(publication_id: int, tags, db: AsyncSession):
#     for tag in tags:
#         logger.info(f'Tags to publication: {type(tag)}')
#         try:
#             insert_stmt = insert(PublicationTagAssociation).values(publication_id=publication_id, tag_id=tag.id)
#             await db.commit()
#         except IntegrityError:
#             pass
#     return tags


# async def get_tag_id_by_name(body, db):
#     stmt = select(Tag).where(Tag.name == body.name)
#     result = await db.execute(stmt)
#     tag = result.unique().scalar_one_or_none()
#     return tag.id


# async def get_tags_for_publication_id(publication_id, db):
#     tag_associations = await db.execute(
#         select(PublicationTagAssociation).filter_by(publication_id=publication_id)
#     )

#     tag_ids = [tag_association.tag_id for tag_association in tag_associations.scalars().all()]
#     tags = []
#     for tag_id in tag_ids:
#         tag = await db.execute(select(Tag).filter_by(id=tag_id))
#         tags.append(tag.unique().scalar_one_or_none())
#         # await db.refresh(tag)
#     return tags


# async def delete_all_tags_from_publication(publication_id, db):
#     for tag in await get_tags_for_publication_id(publication_id, db):
#         await db.delete(tag)

async def create_tag(tag: TagSchema, db: AsyncSession) -> Tag:
    new_tag = Tag(**tag.model_dump(exclude_unset=True))
    db.add(new_tag)
    try:
        await db.commit()
        await db.refresh(new_tag)
    except IntegrityError as e:
        await db.rollback()
    return new_tag


# async def delete_tag_from_publication_by_name(publication_id, body, db):
#     tag_id = await get_tag_id_by_name(body, db)
#     stmt = select(PublicationTagAssociation).filter_by(tag_id=tag_id, publication_id=publication_id)
#     pub_as_tag = await db.execute(stmt)
#     pub_as_tag = pub_as_tag.unique().scalar_one_or_none()
#     if pub_as_tag is not None:
#         await db.delete(pub_as_tag)

async def create_tags(tags: list[TagSchema], db: AsyncSession) -> list[Tag]:
    return [await create_tag(tag, db) for tag in tags]


async def get_tag_by_name(body: TagSchema, db: AsyncSession):
    stmt = select(Tag).filter_by(name=body.name)
    tag = await db.execute(stmt)
    tag = tag.unique().scalar_one_or_none()
    return tag

  
# async def create_tags(body_tags: list[TagBase], db: AsyncSession):
#     """
#     Create tags in database. If tag doesn't exist, create it. If it does exist, do nothing.

#     :param body_tags: list of tags: name of tag from request body in list
#     :param db: database session: AsyncSession
#     :return: list of tags: name of tag from request body in list

#     """

#     tags = []
#     for body in body_tags:
#         stmt = select(Tag).where(Tag.name == body.name)
#         result = await db.execute(stmt)
#         tag = result.unique().scalar_one_or_none()

#         if tag is None:
#             tag = Tag(name=body.name)
#             db.add(tag)
#             await db.commit()
#             await db.refresh(tag)
#         tags.append(tag)
#         logger.info(f'Tag created: {tag.name}')
#     return tags


# async def tags_to_publication_by_id(publication_id: int, tags, db: AsyncSession):
#     """
#     Add tags to publication. If tag doesn't exist, create it. If it does exist, do nothing.

#     :param publication_id: id of publication: int from request body
#     :param tags: list of tags: name of tag from request body in list
#     :param db: database session: AsyncSession
#     :return: list of tags: name of tag from request body in list

#     """
#     for tag in tags:
#         logger.info(f'Tags to publication: {type(tag)}')
#         try:
#             insert_stmt = insert(PublicationTagAssociation).values(publication_id=publication_id, tag_id=tag.id)
#             await db.commit()
#         except IntegrityError:
#             pass
#     return tags


# async def get_tag_id_by_name(body, db):
#     """
#     Get tag id by name.

#     :param body: name of tag from request body in list
#     :param db: database session: AsyncSession
#     :return: id of tag: int from request body

#     """
#     stmt = select(Tag).where(Tag.name == body.name)
#     result = await db.execute(stmt)
#     tag = result.scalar_one_or_none()
#     return tag.id


# async def get_tags_for_publication_id(publication_id, db):
#     """
#     Get tags for publication id.

#     :param publication_id: id of publication: int from request body
#     :param db: database session: AsyncSession
#     :return: list of tags: name of tag from request body in list

#     """
#     tag_associations = await db.execute(
#         select(PublicationTagAssociation).filter_by(publication_id=publication_id)
#     )


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
    if tag is None:
        return None
    stmt = select(PublicationTagAssociation).filter_by(publication_id=publication_id, tag_id=tag.id)
    association = await db.execute(stmt)
    association = association.unique().scalar_one_or_none()
    if association:
        await db.delete(association)
        
# async def delete_all_tags_from_publication(publication_id, db):
#     """
#     Delete all tags from publication.

#     :param publication_id: id of publication: int from request body
#     :param db: database session: AsyncSession
#     :return: None

#     """
#     for tag in await get_tags_for_publication_id(publication_id, db):
#         await db.delete(tag)
#         await db.commit()


# async def delete_tag_from_publication_by_name(publication_id, body, db):
#     """
#     Delete tag from publication.

#     :param publication_id: id of publication: int from request body
#     :param body: name of tag from request body in list
#     :param db: database session: AsyncSession
#     :return: None

#     """
#     tag_id = await get_tag_id_by_name(body, db)
#     stmt = select(PublicationTagAssociation).filter_by(tag_id=tag_id, publication_id=publication_id)
#     pub_as_tag = await db.execute(stmt)
#     pub_as_tag = pub_as_tag.scalar_one_or_none()
#     if pub_as_tag is not None:
#         await db.delete(pub_as_tag)
#         await db.commit()
#     return association

