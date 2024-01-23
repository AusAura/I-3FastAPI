from src.database.models import *
from src.schemas.comments import *
from src.database.db import AsyncSession
from sqlalchemy import func, and_
from typing import List

from sqlalchemy.future import select
from src.utils.my_logger import logger as my_logger


async def add_comment(
        publication_id: int, current_user: User, body: CommentModel, db: AsyncSession
) -> Comment:
    """
    User can add comment for current publication (if exist).
    Receiving publication id and current user.
    :param publication_id: int: publication id received
    :param current_user: User: current user received
    :param body: CommentModel: comment model received
    :param db: AsyncSession: database session received
    :return: Comment: comment added

    """
    comment = Comment(
        user_id=current_user.id,  ## user received
        text=body.text,
        publication_id=publication_id,  ## publication received
    )

    publication = await db.execute(
        select(Publication).filter(Publication.id == publication_id)
    )
    publication = publication.unique().scalar_one_or_none()

    if not publication:
        return None

    my_logger.info(
        "Comment added - ID: %s, User ID: %s, Text: %s, Publication ID: %s, Created At: %s, Updated At: %s",
        comment.id,
        comment.user_id,
        comment.text,
        comment.publication_id,
        comment.created_at,
        comment.updated_at,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    return comment


async def edit_comment(
        comment_id: int, body: CommentModelEditing, current_user: User, db: AsyncSession
) -> Comment | None:
    """
    Editing comment only for current user's publication.
    Receiving comment id and current user.
    :param comment_id: int: comment id to edit
    :param body: CommentModel: comment model with new text
    :param current_user: User: current user (creator of publication)
    :param db: AsyncSession: database session
    :return: Comment: comment edited

    """
    comment = await db.execute(
        select(Comment).filter(
            and_(Comment.user_id == current_user.id, Comment.id == comment_id)
        )
    )
    comment = comment.scalar_one_or_none()

    my_logger.info(body.text)
    if comment:
        comment.text = body.text
        await db.commit()
        await db.refresh(comment)

    return comment


async def delete_comment(
        comment_id: int, current_user: User, db: AsyncSession
) -> Comment | None:
    """
    (Admin only) Delete comment.
    Receiving comment id and current user.
    :param comment_id: int: comment id to delete from db
    :param current_user: User: current user (creator of publication)
    :param db: AsyncSession: database session
    :return: Comment: comment deleted from db

    """
    comment = await db.execute(
        select(Comment).filter(
            and_(Comment.user_id == current_user.id, Comment.id == comment_id)
        )
    )
    comment = comment.scalar_one_or_none()

    if comment:
        await db.delete(comment)
        await db.commit()

    return comment


async def get_comments(
        publication_id: int, skip: int, limit: int, db: AsyncSession
) -> List[Comment]:
    """
    (Any) Get all comments.
    Receiving publication id.
    :param publication_id: int: publication id to get comments from db
    :param skip: int: offset for pagination
    :param limit: int: limit for pagination
    :param db: AsyncSession: database session
    :return: List[Comment]: list of comments from db

    """
    comment = await db.execute(
        select(Comment)
        .filter(Comment.publication_id == publication_id)
        .offset(skip)
        .limit(limit)
        .order_by(Comment.created_at)
    )
    comment = comment.unique().scalars().all()
    return comment


async def get_comment(
        comment_id: int, db: AsyncSession
) -> Comment | None:
    """
    (Any) Get one comment.
    Receiving comment id.
    :param comment_id: int: comment id to get from db
    :param db: AsyncSession: database session
    :return: Comment | None: comment from db or None

    """
    comment = await db.execute(
        select(Comment).filter(Comment.id == comment_id)
    )
    comment = comment.unique().scalar_one_or_none()
    return comment
