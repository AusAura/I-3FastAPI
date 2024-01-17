from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from src.database.db import get_db
from src.database.models import User, Tag
from src.repositories import tags as repositories_tags
from src.repositories import publications as repositories_publications
from src.services.auth import auth_service
from src.schemas.tags import TagBase, TagPublication, TagCreate
import src.messages as msg

router = APIRouter(prefix='/tags', tags=['Tags'])


@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=list[TagPublication])
async def create_tags(tags: list[TagCreate], db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    created_tags = await repositories_tags.create_tags(tags, db)
    return [{"id": tag.id, "name": tag.name} for tag in created_tags]


@router.post('/add_to_publication', status_code=status.HTTP_200_OK, response_model=list[TagPublication])
async def add_tags_to_publication(publication_id: int, tags: list[TagBase], db: AsyncSession = Depends(get_db),
                                  user: User = Depends(auth_service.get_current_user)):
    publication = await repositories_publications.get_publication(publication_id, db, user)

    if publication is None:
        raise HTTPException(status_code=404, detail=msg.PUBLICATION_NOT_FOUND)

    existing_tags = set(tag.name for tag in publication.tags)
    new_tags = [tag for tag in tags if tag.name not in existing_tags]

    if len(publication.tags) + len(new_tags) > 5:
        raise HTTPException(status_code=400, detail="Exceeded the maximum allowed tags for a publication (5).")

    added_tags = await repositories_tags.create_tags(new_tags, db)
    publication = await repositories_tags.append_tags_to_publication(publication, added_tags)

    return [{"id": tag.id, "name": tag.name} for tag in publication.tags]


@router.delete('/remove_from_publication', status_code=status.HTTP_200_OK, response_model=list[TagPublication])
async def remove_tags_from_publication(publication_id: int, tags: list[TagBase], db: AsyncSession = Depends(get_db),
                                       user: User = Depends(auth_service.get_current_user), repositories=None):
    publication = await repositories_publications.get_publication(publication_id, db, user)

    if publication is None:
        raise HTTPException(status_code=404, detail=msg.PUBLICATION_NOT_FOUND)

    tags_to_remove = [tag for tag in publication.tags if tag.name in [t.name for t in tags]]

    if not tags_to_remove:
        raise HTTPException(status_code=400, detail="No matching tags found to remove from the publication.")

    publication = await repositories_tags.delete_tags_from_publication(publication, tags_to_remove, db)

    return [{"id": tag.id, "name": tag.name} for tag in publication.tags]
