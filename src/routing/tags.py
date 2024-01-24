from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.database.db import get_db
from src.database.models import User
from src.repositories import tags as repositories_tags
from src.repositories import publications as repositories_publications
from src.services.auth import auth_service
from src.schemas.tags import TagSchema, TagsDetailResponse
import src.messages as msg

router = APIRouter(prefix='/publications', tags=['tags'])


@router.post('/{publication_id}/tags', status_code=status.HTTP_201_CREATED, response_model=TagsDetailResponse,
             description='Add a new tag to pub by id')
async def add_tag_to_publication(publication_id: int, body: TagSchema, db: AsyncSession = Depends(get_db),
                                 user: User = Depends(auth_service.get_current_user)):
    """
    Add a new tag to pub by id from request body.

    :param publication_id: id of publication: int from request body
    :param body: name of tag from request body in list
    :param db: database session: AsyncSession
    :return: publication

    """

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
        "detail": msg.TAG_ASSOCIATION_ADDED + f"{publication_id}",
        "tag": tag
    }


@router.delete('/{publication_id}/tags', response_model=TagsDetailResponse,
               description='Delete tag from pub by id')
async def delete_tag_from_publication(publication_id: int, body: TagSchema, db: AsyncSession = Depends(get_db),
                                      user: User = Depends(auth_service.get_current_user)):
  
    publication = await repositories_publications.get_publication_by_id(publication_id, db, user)
    if publication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)
    association = await repositories_tags.delete_tag_from_publication(publication_id, body, db)
    if association is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.TAG_NOT_FOUND)
    return {
        "detail": msg.TAG_ASSOCIATION_DELETED + f"{publication_id}",
        "tag": body
    } 
  
#         raise HTTPException(status_code=404, detail=msg.PUBLICATION_NOT_FOUND)

#     tags = await repositories_tags.create_tags([body], db)
#     insert_stmt = insert(PublicationTagAssociation).values(publication_id=publication_id, tag_id=tags[0].id)
#     await db.commit()
#     await db.refresh(publication)
#     return publication


# @router.post('/create', status_code=status.HTTP_201_CREATED, response_model=list[TagPublication])
# async def create_tags(tags: list[TagCreate], db: AsyncSession = Depends(get_db),
#                       user: User = Depends(auth_service.get_current_user)):
#     """
#     Create tags in database. If tag doesn't exist, create it. If it does exist, do nothing.

#     :param tags: list of tags: name of tag from request body in list
#     :param db: database session: AsyncSession
#     :return: list of tags: name of tag from request body in list


#     """
#     created_tags = await repositories_tags.create_tags(tags, db)
#     return [{"id": tag.id, "name": tag.name} for tag in created_tags]


# @router.get("/{publication_id}", status_code=status.HTTP_200_OK, response_model=list[TagBase])
# async def get_tags_for_publication(publication_id: int, db: AsyncSession = Depends(get_db),
#                                    user: User = Depends(auth_service.get_current_user)):
#     """
#     Get tags for publication by id.

#     :param publication_id: id of publication: int from request body
#     :param db: database session: AsyncSession
#     :return: list of tags: name of tag from request body in list


#     """
#     tags = await repositories_tags.get_tags_for_publication_id(publication_id, db)
#     return tags


# @router.delete('/{publication_id}/delete_tag', status_code=status.HTTP_204_NO_CONTENT)
# async def remove_tags_from_publication(publication_id: int, body: TagBase, db: AsyncSession = Depends(get_db),
#                                        user: User = Depends(auth_service.get_current_user)):
#     """
#     Remove tag from publication by name.

#     :param publication_id: id of publication: int from request body
#     :param body: name of tag from request body in list
#     :param db: database session: AsyncSession
#     :return: list of tags: name of tag from request body in list

#     """


#         raise HTTPException(status_code=404, detail=msg.PUBLICATION_NOT_FOUND)
#     publication = await repositories_tags.delete_tag_from_publication_by_name(publication_id, body, db)
#     return {"detail": body.name + " " + msg.TAG_ASSOCIATION_DELETED}


# @router.delete('/{publication_id}/delete_all_tags', status_code=status.HTTP_204_NO_CONTENT)
# async def remove_all_tags_from_publication(publication_id: int, db: AsyncSession = Depends(get_db),
#                                            user: User = Depends(auth_service.get_current_user)):
#     """
#     Remove all tags from publication by id.

#     :param publication_id: id of publication: int from request body
#     :param db: database session: AsyncSession
#     :return: list of tags: name of tag from request body in list

#     """
#     publication = await repositories_publications.get_publication_by_id(publication_id, db, user)

#     if publication is None:
#         raise HTTPException(status_code=404, detail=msg.PUBLICATION_NOT_FOUND)

#     # Assuming you have a repository method to delete all tags from a publication
#     await repositories_tags.delete_all_tags_from_publication(publication_id, db)

#     return {"detail": "All tags removed from the publication with ID: " + str(publication_id)}
