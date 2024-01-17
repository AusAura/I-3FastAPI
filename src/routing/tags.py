from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from src.database.db import get_db
from src.database.models import User, Tag, Publication, PublicationTagAssociation
from src.repositories import tags as repositories_tags
from src.repositories import publications as repositories_publications
from src.schemas.publications import PublicationResponse
from src.services.auth import auth_service
from src.schemas.tags import TagBase, TagPublication, TagCreate
import src.messages as msg

router = APIRouter(prefix='/tags', tags=['Tags'])


@router.put('/add_to_publication', response_model=PublicationResponse, status_code=201,
            description='Add a new tag to pub by id')
async def add_tag_to_publication(publication_id: int, body: TagBase, db: AsyncSession = Depends(get_db),
                                 user: User = Depends(auth_service.get_current_user)):
    stmt = select(Publication).filter_by(id=publication_id, user=user)
    publication = await db.execute(stmt)
    publication = publication.scalar_one_or_none()
    if publication is None:
        raise HTTPException(status_code=404, detail=msg.PUBLICATION_NOT_FOUND)

    tags = await repositories_tags.create_tags([body], db)
    insert_stmt = insert(PublicationTagAssociation).values(publication_id=publication_id, tag_id=tags[0].id)
    await db.commit()
    await db.refresh(publication)
    return publication


@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=list[TagPublication])
async def create_tags(tags: list[TagCreate], db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    created_tags = await repositories_tags.create_tags(tags, db)
    return [{"id": tag.id, "name": tag.name} for tag in created_tags]

# @router.post('/add_to_publication', status_code=status.HTTP_200_OK, response_model=list[TagPublication])
# async def add_tags_to_publication(publication_id: int, tags: list[TagBase], db: AsyncSession = Depends(get_db),
#                                   user: User = Depends(auth_service.get_current_user)):
#     publication = await repositories_publications.get_publication(publication_id, db, user)
#
#     if publication is None:
#         raise HTTPException(status_code=404, detail=msg.PUBLICATION_NOT_FOUND)
#
#     existing_tags = set(tag.name for tag in publication.tags)
#     # existing_tags = set(tag.name for tag in publication.tags) if publication.tags else set()
#
#     new_tags = [tag for tag in tags if tag.name not in existing_tags]
#
#     if len(publication.tags) + len(new_tags) > 5:
#         raise HTTPException(status_code=400, detail="Exceeded the maximum allowed tags for a publication (5).")
#
#     added_tags = await repositories_tags.create_tags(new_tags, db)
#     publication = await repositories_tags.append_tags_to_publication(publication, added_tags)
#
#     return [{"id": tag.id, "name": tag.name} for tag in publication.tags]
#
#
@router.delete('/remove_from_publication{publication_id}')
async def remove_tags_from_publication(publication_id: int, body: TagBase, db: AsyncSession = Depends(get_db),
                                       user: User = Depends(auth_service.get_current_user)):
    publication = await repositories_publications.get_publication(publication_id, db, user)

    if publication is None:
        raise HTTPException(status_code=404, detail=msg.PUBLICATION_NOT_FOUND)

    publication = await repositories_tags.delete_tag_from_publication_by_name(publication_id, body, db)

    return {"detail": body.name + " " + msg.TAG_ASSOCIATION_DELETED}
