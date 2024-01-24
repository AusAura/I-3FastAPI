from typing import List

from src.database.models import Role
from src.messages import *
from src.schemas.comments import *
from src.database.db import get_db, AsyncSession
from src.services.auth import auth_service
from src.database.models import User
from src.repositories import comments as repository_comments

# from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, HTTPException, Depends, status, Query

router = APIRouter(prefix="/publications", tags=["comments"])


@router.get(
    "/{publication_id}/comments",
    response_model=List[CommentModelReturned],
    description="No more than 100 requests per minute",
    dependencies=[],
)  # Depends(RateLimiter(times=100, seconds=60))
async def read_comments(
    publication_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=0, le=500),
    db: AsyncSession = Depends(get_db),
):
    """
    Get comments by publication id and skip and limit parameters

    :param publication_id: int: id of publication to get comments
    :param skip: int: number of comments to skip from the beginning of the list
    :param limit: int: number of comments to return from the beginning of the list
    :param db: AsyncSession: database session
    :return: List[CommentModelReturned]: list of comments

    """
    comments = await repository_comments.get_comments(publication_id, skip, limit, db)

    if list(comments):
        return comments
    else:
        raise HTTPException(404, COMMENTS_NOT_FOUND)


@router.get(
    "/{publication_id}/comments/{comment_id}",
    response_model=CommentModelReturned,
    description="No more than 100 requests per minute",
    dependencies=[],
)  # Depends(RateLimiter(times=100, seconds=60))
async def read_comment(
    comment_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Get comment by comment id

    :param comment_id: int: id of comment to get
    :param db: AsyncSession: database session
    :return: CommentModelReturned: comment

    """
    comment = await repository_comments.get_comment(comment_id, db)
    if comment:
        return comment
    else:
        raise HTTPException(404, COMMENT_NOT_FOUND)


@router.post(
    "/{publication_id}/comments/add",
    response_model=CommentResponceAdded,
    status_code=status.HTTP_201_CREATED,
    description="No more than 100 requests per minute",
    dependencies=[],
)  # Depends(RateLimiter(times=100, seconds=60))
async def add_comment(
    publication_id: int,
    body: CommentModelEditing,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Add comment by publication id and body

    :param publication_id: int: id of publication to add comment
    :param body: CommentModelEditing: body of comment to add
    :param db: AsyncSession: database session
    :param current_user: User: current user from auth service
    :return: CommentResponceAdded: comment added to publication

    """
    comment = await repository_comments.add_comment(
        publication_id, current_user, body, db
    )
    if comment:
        return {"comment": comment, "detail": COMMENT_SUCCESSFULLY_ADDED}
    else:
        raise HTTPException(404, PUBLICATION_NOT_FOUND)


@router.patch(
    "/{publication_id}/comments/{comment_id}/edit",
    response_model=CommentResponceEdited,
    status_code=status.HTTP_202_ACCEPTED,
    description="No more than 10 requests per minute",
    dependencies=[],
)  # Depends(RateLimiter(times=10, seconds=60))
async def edit_comment(
    comment_id: int,
    body: CommentModelEditing,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Edit comment by comment id and body

    :param comment_id: int: id of comment to edit
    :param body: CommentModelEditing: body of comment to edit
    :param db: AsyncSession: database session
    :param current_user: User: current user from auth service
    :return: CommentResponceEdited: comment edited

    """
    comment = await repository_comments.edit_comment(comment_id, body, current_user, db)
    if comment:
        print(comment.id, comment.text, comment.created_at, comment.publication_id)
        return {"comment": comment, "detail": COMMENT_SUCCESSFULLY_EDITED}
    else:
        raise HTTPException(403, VERIFICATION_ERROR)


@router.delete(
    "/{publication_id}/comments/{comment_id}/delete",
    # response_model=CommentResponceDeleted,
    status_code=status.HTTP_204_NO_CONTENT,
    description="No more than 10 requests per minute",
    dependencies=[],
)  # Depends(RateLimiter(times=10, seconds=60))
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):  
    """
    Delete comment by comment id

    :param comment_id: int: id of comment to delete
    :param db: AsyncSession: database session
    :param current_user: User: current user from auth service
    :return: CommentResponceDeleted: comment deleted

    """

    if current_user.role == Role.admin or current_user.role == Role.moderator:
        comment = await repository_comments.delete_comment(comment_id, current_user, db)
    else:
        raise HTTPException(403, VERIFICATION_ERROR)

    if not comment:
        raise HTTPException(404, COMMENT_NOT_FOUND)
