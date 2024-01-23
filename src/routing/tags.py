from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from src.database.db import get_db
from src.database.models import User, PublicationTagAssociation
from src.repositories import tags as repositories_tags
from src.repositories import publications as repositories_publications
from src.services.auth import auth_service
from src.schemas.tags import TagSchema, TagsDetailResponse
import src.messages as msg

router = APIRouter(prefix='/publications', tags=['tags'])


@router.put('/{publication_id}/tags/add_one', status_code=status.HTTP_201_CREATED, response_model=TagsDetailResponse,
            description='Add a new tag to pub by id')
async def add_tag_to_publication(publication_id: int, body: TagSchema, db: AsyncSession = Depends(get_db),
                                 user: User = Depends(auth_service.get_current_user)):

    publication = await repositories_publications.get_publication_by_id(publication_id, db, user)
    if publication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)
    if len(publication.tags) == 5:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg.TAGS_LIMIT_EXCEEDED)
    if body.name in [tag.name for tag in publication.tags]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg.TAG_ALREADY_EXISTS)

    tag = await repositories_tags.create_tag(body, db)
    tag = await repositories_tags.publication_extend_tag(publication_id, body, db)
    return {
        "detail": f"add tag[s] to publication with id:{publication_id}",
        "tag": tag
    }



