from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from src.database.db import get_db
from src.database.models import User, PublicationTagAssociation
from src.repositories import tags as repositories_tags
from src.repositories import publications as repositories_publications
from src.schemas.publications import PublicationResponse
from src.services.auth import auth_service
from src.schemas.tags import TagSchema, TagPublication, TagCreate
import src.messages as msg


router = APIRouter(prefix='/publications/tags', tags=['Tags'])


@router.put('/add_one', response_model=PublicationResponse, status_code=201,
            description='Add a new tag to pub by id')
async def add_tag_to_publication(publication_id: int, body: TagSchema, db: AsyncSession = Depends(get_db),
                                 user: User = Depends(auth_service.get_current_user)):

    publication = await repositories_publications.get_publication_by_id(publication_id, db, user)
    if publication is None:
        raise HTTPException(status_code=404, detail=msg.PUBLICATION_NOT_FOUND)

    tags = await repositories_tags.create_tags([body], db)

    return publication


@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=list[TagPublication])
async def create_tags(tags: list[TagCreate], db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    created_tags = await repositories_tags.create_tags(tags, db)
    return [{"id": tag.id, "name": tag.name} for tag in created_tags]


@router.get("/{publication_id}", status_code=status.HTTP_200_OK, response_model=list[TagSchema])
async def get_tags_for_publication(publication_id: int, db: AsyncSession = Depends(get_db),
                                   user: User = Depends(auth_service.get_current_user)):
    tags = await repositories_tags.get_tags_for_publication_id(publication_id, db)
    return tags


@router.delete('/{publication_id}/delete_tag', status_code=status.HTTP_204_NO_CONTENT)
async def remove_tags_from_publication(publication_id: int, body: TagSchema, db: AsyncSession = Depends(get_db),
                                       user: User = Depends(auth_service.get_current_user)):
    publication = await repositories_publications.get_publication_by_id(publication_id, db, user)

    if publication is None:
        raise HTTPException(status_code=404, detail=msg.PUBLICATION_NOT_FOUND)

    publication = await repositories_tags.delete_tag_from_publication_by_name(publication_id, body, db)

    return {"detail": body.name + " " + msg.TAG_ASSOCIATION_DELETED}


@router.delete('/{publication_id}/delete_all_tags', status_code=status.HTTP_204_NO_CONTENT)
async def remove_all_tags_from_publication(publication_id: int, db: AsyncSession = Depends(get_db),
                                           user: User = Depends(auth_service.get_current_user)):
    publication = await repositories_publications.get_publication_by_id(publication_id, db, user)

    if publication is None:
        raise HTTPException(status_code=404, detail=msg.PUBLICATION_NOT_FOUND)

    # Assuming you have a repository method to delete all tags from a publication
    await repositories_tags.delete_all_tags_from_publication(publication_id, db)

    return {"detail": "All tags removed from the publication with ID: " + str(publication_id)}
