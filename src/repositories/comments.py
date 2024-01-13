from src.database.models import *
from src.schemas.comments import *
from src.database.db import AsyncSession
from sqlalchemy import func, and_
from typing import List

dummy_user = User(
    id=0,
    username='Josh Dummy',
    email='joshdummy@gmail.com',
    password='iafshgsgisuhgishg',
    avatar='ahfoshgiushgiusghgs',
    refresh_token='ahfhsdighsighs',
    role=Role.user,
    is_active=True,
    confirmed=True,
    created_at=DateTime(),
    updated_at=DateTime()
)

user = dummy_user

dummy_publication = Publication(
    id=1,
    user_id=user.id,
    pub_image_id=0,
    title='Dummy title',
    description='I am a dummy mummy',
    created_at=DateTime(),
    updated_at=DateTime()
)

publication = dummy_publication
####

async def add_comment(body: CommentModel, user: User, db: AsyncSession) -> Comment:
    comment = Comment(
        id=body.id,
        username=body.user.username,
        text=body.text,
        publication_id=body.publication_id,
        created_at=body.created_at,
        updated_at=body.updated_at
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment

async def edit_comment(comment_id: int, body: CommentModel, user: User, db: AsyncSession) -> Comment | None:
    comment = db.query(Comment).filter(and_(Comment.user_id == user.id, Comment.id == comment_id)).first()
    if comment:
        comment.id=body.id,
        comment.username=body.user.username,
        comment.text=body.text,
        comment.publication_id=body.publication_id,
        comment.created_at=body.created_at,
        comment.updated_at=body.updated_at
        db.commit()

    return comment

async def delete_comment(comment_id: int, user: User, db: AsyncSession) -> Comment | None:
    comment = db.query(Comment).filter(and_(Comment.user_id == user.id, Comment.id == comment_id)).first()
    if comment:
        db.delete(comment)
        db.commit()

    return comment


async def get_comments(publication_id: int, skip: int, limit: int, user: User, db: AsyncSession) -> List[Comment]:
    return db.query(Comment).filter(Comment.publication_id == publication.id).offset(skip).limit(limit).order_by(Comment.created_at).all()


async def get_comment(publication_id: int, query: str, user: User, db: AsyncSession) -> Comment:
    result = db.query(Comment).filter(and_(Comment.publication_id == publication_id, Comment.user_id == user.id)).first()
    return result