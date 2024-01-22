from typing import List

from src.database.models import Role
from src.messages import *
from src.schemas.comments import *
from src.database.db import get_db, AsyncSession
from src.services.auth import auth_service
from src.database.models import User
from src.repositories import comments as repository_comments

from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Request

router = APIRouter(prefix="/publications", tags=["comments"])


@router.get(
    "/{publication_id}/comments",
    response_model=List[CommentModelReturned],
    description="No more than 100 requests per minute",
    dependencies=[],
)  # Depends(RateLimiter(times=100, seconds=60))
async def read_comments(
    publication_id: int,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    comments = await repository_comments.get_comments(publication_id, skip, limit, db)
    if comments:
        return comments
    else:
        raise HTTPException(404, PUBLICATION_NOT_FOUND)


@router.get(
    "/{publication_id}/comments/{comment_id}",
    response_model=CommentModelReturned,
    description="No more than 100 requests per minute",
    dependencies=[],
)  # Depends(RateLimiter(times=100, seconds=60))
async def read_comment(
    comment_id: int, db: AsyncSession = Depends(get_db)
):  ### publication_id: int,
    comment = await repository_comments.get_comment(comment_id, db)  ### publication_id,
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
    comment = await repository_comments.edit_comment(comment_id, body, current_user, db)
    if comment:
        print(comment.id, comment.text, comment.created_at, comment.publication_id)
        return {"comment": comment, "detail": COMMENT_SUCCESSFULLY_EDITED}
    else:
        raise HTTPException(403, VERIFICATION_ERROR)


@router.delete(
    "/{publication_id}/comments/{comment_id}/delete",
    response_model=CommentResponceDeleted,
    status_code=status.HTTP_204_NO_CONTENT,
    description="No more than 10 requests per minute",
    dependencies=[],
)  # Depends(RateLimiter(times=10, seconds=60))
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):  
    if current_user.role == Role.admin:
        comment = await repository_comments.delete_comment(comment_id, current_user, db)
    else:
        raise HTTPException(403, VERIFICATION_ERROR)

    if comment:
        return {"comment": comment, "detail": COMMENT_SUCCESSFULLY_DELETED}
    else:
        raise HTTPException(404, COMMENT_NOT_FOUND)
