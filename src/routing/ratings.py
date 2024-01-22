from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.database.db import get_db
from src.database.models import User, Publication, Rating, Role
from src.repositories import publications as repositories_publications
from src.repositories import ratings as repositories_ratings
from src.schemas.ratings import RatingCreate, RatingResponse
from src.schemas.user import UserResponse
from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.utils.my_logger import logger
import src.messages as msg

router = APIRouter(tags=['rating'])
access_to_route = RoleAccess([Role.admin, Role.moderator])


# all roles
@router.post('/publications/{publication_id}/rating/add', status_code=status.HTTP_201_CREATED,
             response_model=RatingResponse)
async def add_rating(publication_id: int, body: RatingCreate, db: AsyncSession = Depends(get_db),
                     user: User = Depends(auth_service.get_current_user)):
    publication = await repositories_publications.get_publication_by_id(publication_id, db)
    if publication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)

    if user.id == publication.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg.OWN_PUBLICATION)

    try:
        rating = await repositories_ratings.add_rating(publication_id, body, db, user)
        return rating
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg.ALREADY_VOTED_PUBLICATION)


# all roles
@router.get('/publications/{publication_id}/rating/users', status_code=status.HTTP_200_OK,
            response_model=list[UserResponse])
async def get_users_ratings_by_publication_id(publication_id: int, db: AsyncSession = Depends(get_db),
                                              limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                                              user: User = Depends(auth_service.get_current_user)):

    publication = await repositories_publications.get_publication_by_id(publication_id, db, user)
    if publication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)

    users = await repositories_ratings.get_users_by_ratings(publication.ratings, db, limit, offset)
    return users


# admin, moderator only
@router.get('/admin/users/{user_id}/ratings', status_code=status.HTTP_200_OK, response_model=list[RatingResponse],
            dependencies=[Depends(access_to_route)])
async def get_user_ratings(user_id: int, db: AsyncSession = Depends(get_db),
                           limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                           user: User = Depends(auth_service.get_current_user)):

    ratings = await repositories_ratings.get_all_ratings_by_user_id(user_id, db, limit, offset)
    return ratings


# admin, moderator only
@router.delete('/publications/{publication_id}/ratings/{user_id}/delete', status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(access_to_route)])
async def delete_rating(user_id: int, publication_id: int, db: AsyncSession = Depends(get_db),
                        user: User = Depends(auth_service.get_current_user)):

    rating = await repositories_ratings.delete_rating(user_id, publication_id, db)
    if rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.RATING_NOT_FOUND)

    return {"message": msg.RATING_DELETED}
