from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.tags import TagCreate, TagUpdate, TagPublication, TagBase
from src.schemas.publications import PublicationResponse
from src.repositories import tags as repository_tags
from src.database.db import get_db
from src.services.auth import auth_service
from src.database.models import User, Publication
import src.messages as msg

router = APIRouter(prefix='/tags', tags=['tags'])


@router.put('/add_to_publication', response_model=PublicationResponse, status_code=201,
            description='Add a new tag to pub by id')
async def add_tag_to_publication(publication_id: int, body: TagBase, db: AsyncSession = Depends(get_db),
                                 user: User = Depends(auth_service.get_current_user)):
    stmt = select(Publication).filter_by(id=publication_id, user=user)
    publication = await db.execute(stmt)
    publication = publication.scalar_one_or_none()
    if publication is None:
        raise HTTPException(status_code=404, detail=msg.PUBLICATION_NOT_FOUND)
    if len(publication.tags) == 5:
        raise HTTPException(status_code=400, detail=msg.TAGS_LIMIT_EXCEEDED)
    tags = await repository_tags.create_tags([body], db)
    publication = await repository_tags.append_tags_to_publication(publication, tags)
    await db.commit()
    await db.refresh(publication)
    return publication

# @router.post('/add', response_model=TagPublication, status_code=201, description='Add a new tag')
# async def add_tag(tag: TagCreate, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
#     created_tag = await repository_tags.add_tag(tag, db)
#     return created_tag
#
# @router.delete('/{tag_id}/delete', response_model=None, status_code=204, description='Delete a tag by ID')
# async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
#     await repository_tags.delete_tag(tag_id, db)
#     return None
#
# @router.get('/{tag_id}', response_model=TagPublication, description='Get a tag by ID')
# async def get_tag(tag_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
#     tag = await repository_tags.get_tag(tag_id, db)
#     if tag is not None:
#         return tag
#     else:
#         raise HTTPException(status_code=404, detail=msg.TAG_NOT_FOUND)
#
# @router.get('/', response_model=List[TagPublication], description='Get all tags')
# async def get_tags(db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
#     tags = await repository_tags.get_tags(db)
#     return tags
#
# @router.patch('/{tag_id}/edit', response_model=TagPublication, description='Edit a tag by ID')
# async def edit_tag(tag_id: int, tag_update: TagUpdate, db: AsyncSession = Depends(get_db),
#                    user: User = Depends(auth_service.get_current_user)):
#     edited_tag = await repository_tags.edit_tag(tag_id, tag_update, db)
#     if edited_tag is not None:
#         return edited_tag
#     else:
#         raise HTTPException(status_code=404, detail=msg.TAG_NOT_FOUND)
