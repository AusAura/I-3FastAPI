from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.database.db import get_db
from src.database.models import User, Publication, Rating, Role
from src.repositories import publications as repositories_publications
from src.repositories import ratings as repositories_ratings
from src.repositories import users as repository_users
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
    """
    Add rating to publication by user if not exists else update rating by user if exists

    :param publication_id: int: id of publication to add rating
    :param body: RatingCreate: rating data to add or update by user if exists in database
    :param db: AsyncSession: database session
    :param user: User: current user
    :return: RatingResponse: rating data with user data

    """
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


# all roles,  if admin, moderator user - any
@router.get('/publications/{publication_id}/rating/users', status_code=status.HTTP_200_OK,
            response_model=list[UserResponse])
async def get_users_ratings_by_publication_id(publication_id: int, db: AsyncSession = Depends(get_db),
                                              limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                                              user: User = Depends(auth_service.get_current_user)):
    """
    Get all users who rated publication by id

    :param publication_id: int: id of publication to get users who rated
    :param db: AsyncSession: database session
    :param limit: int: limit of users who rated publication
    :param offset: int: offset of users who rated publication
    :param user: User: current user
    :return: list[UserResponse]: list of users who rated publication

    """
    if user.role != Role.user:
        user = repository_users.get_user_by_publication_id(publication_id, db)

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
    """
    Get all ratings by user id

    :param user_id: int: id of user to get ratings
    :param db: AsyncSession: database session
    :param limit: int: limit of ratings

    """

    ratings = await repositories_ratings.get_all_ratings_by_user_id(user_id, db, limit, offset)
    return ratings


# admin, moderator only
@router.delete('/publications/{publication_id}/ratings/{user_id}/delete', status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(access_to_route)])
async def delete_rating(user_id: int, publication_id: int, db: AsyncSession = Depends(get_db),
                        user: User = Depends(auth_service.get_current_user)):
    """
    Delete rating by user id and publication id

    :param user_id: int: id of user to delete rating
    :param publication_id: int: id of publication to delete rating
    :param db: AsyncSession: database session
    :param user: User: current user
    :return: None

    """

    rating = await repositories_ratings.delete_rating(user_id, publication_id, db)
    if rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.RATING_NOT_FOUND)

    return rating
