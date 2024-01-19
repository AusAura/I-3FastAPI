from src.database.models import *
from src.schemas.comments import *
from src.database.db import AsyncSession
from sqlalchemy import func, and_
from typing import List

from sqlalchemy.future import select
from src.utils.my_logger import logger as my_logger

# dummy_user = User(
#     id=1,
#     username='Josh Dummy',
#     email='joshdummy@gmail.com',
#     password='iafshgsgisuhgishg',
#     avatar='ahfoshgiushgiusghgs',
#     refresh_token='ahfhsdighsighs',
#     role=Role.admin,
#     is_active=True,
#     confirmed=True,
#     created_at=DateTime(),
#     updated_at=DateTime()
# )

# user = dummy_user

# dummy_publication = Publication(
#     id=1,
#     user_id=user.id,
#     title='Dummy title',
#     description='I am a dummy mummy',
#     created_at=DateTime(),
#     updated_at=DateTime()
# )

# publication = dummy_publication
####


async def add_comment(publication_id: int, current_user: User, body: CommentModel, db: AsyncSession) -> Comment:
    '''
    User can add comment only for his publication.
    '''
    comment = Comment(
        user_id=current_user.id, ## user received
        text=body.text,
        publication_id=publication_id, ## publication received
        # created_at=body.created_at,
        # updated_at=body.updated_at
    )

    my_logger.info(
    "Comment added - ID: %s, User ID: %s, Text: %s, Publication ID: %s, Created At: %s, Updated At: %s",
    comment.id, comment.user_id, comment.text, comment.publication_id, comment.created_at, comment.updated_at
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    return comment


async def edit_comment(comment_id: int, body: CommentModelEditing, current_user: User, db: AsyncSession) -> Comment | None:
    '''
    Editing comment only for current user's publication.
    Receiving comment id and current user.
    '''
    comment = await db.execute(select(Comment).filter(and_(Comment.user_id == current_user.id, Comment.id == comment_id)))
    comment = comment.scalar_one_or_none()

    my_logger.info(body.text)
    if comment:
        comment.text=body.text
        await db.commit()
        await db.refresh(comment)

    return comment


async def delete_comment(comment_id: int, current_user: User, db: AsyncSession) -> Comment | None:
    '''
    (Admin only) Delete comment.
    Receiving comment id and current user.
    '''
    comment = await db.execute(select(Comment).filter(and_(Comment.user_id == current_user.id, Comment.id == comment_id)))
    comment = comment.scalar_one_or_none()
        
    if comment:
        await db.delete(comment)
        await db.commit()

    return comment


async def get_comments(publication_id: int, skip: int, limit: int, db: AsyncSession) -> List[Comment]:
    '''
    (Any) Get all comments.
    Receiving publication id.
    '''
    comment = await db.execute(select(Comment).filter(Comment.publication_id == publication_id).offset(skip).limit(limit).order_by(Comment.created_at))
    comment = comment.scalars()
    return comment


async def get_comment(comment_id: int, db: AsyncSession) -> Comment | None: ## publication_id: int, 
    '''
    (Any) Get one comment.
    Receiving comment id.
    '''
    comment = await db.execute(select(Comment).filter(Comment.id == comment_id)) ### and_(Comment.publication_id == publication_id, Comment.user_id == user.id,)
    comment = comment.scalar_one_or_none()
    return comment