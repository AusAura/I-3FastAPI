from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.tags import TagCreate, TagUpdate, TagResponse  # Update this import line
from src.repositories import tags as repository_tags
from src.database.db import get_db
from src.services.auth import auth_service
from src.database.models import User
from src.messages import *

router = APIRouter(prefix='/tags', tags=['tags'])

@router.post('/add', response_model=TagResponse, status_code=201, description='Add a new tag')
async def add_tag(tag: TagCreate, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    created_tag = await repository_tags.add_tag(tag, db)
    return created_tag

@router.delete('/{tag_id}/delete', response_model=None, status_code=204, description='Delete a tag by ID')
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    await repository_tags.delete_tag(tag_id, db)
    return None

@router.get('/{tag_id}', response_model=TagResponse, description='Get a tag by ID')
async def get_tag(tag_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    tag = await repository_tags.get_tag(tag_id, db)
    if tag is not None:
        return tag
    else:
        raise HTTPException(status_code=404, detail=TAG_NOT_FOUND)

@router.get('/', response_model=List[TagResponse], description='Get all tags')
async def get_tags(db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    tags = await repository_tags.get_tags(db)
    return tags

@router.patch('/{tag_id}/edit', response_model=TagResponse, description='Edit a tag by ID')
async def edit_tag(tag_id: int, tag_update: TagUpdate, db: AsyncSession = Depends(get_db),
                   user: User = Depends(auth_service.get_current_user)):
    edited_tag = await repository_tags.edit_tag(tag_id, tag_update, db)
    if edited_tag is not None:
        return edited_tag
    else:
        raise HTTPException(status_code=404, detail=TAG_NOT_FOUND)
