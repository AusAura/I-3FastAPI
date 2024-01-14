from datetime import datetime, date
from pydantic import BaseModel, Field, EmailStr

from src import messages

class CommentModelEditing(BaseModel):
    text: str

    class Config:
        orm_mode = True


class CommentModel(CommentModelEditing):

    created_at: datetime
    updated_at: datetime
    

class CommentModelReturned(CommentModel):
    id: int
    user_id: int
    publication_id: int


class CommentResponceAdded(BaseModel):
    comment: CommentModelReturned
    detail: str = messages.COMMENT_SUCCESSFULLY_ADDED

class CommentResponceEdited(BaseModel):
    comment: CommentModelReturned
    detail: str = messages.COMMENT_SUCCESSFULLY_EDITED

class CommentResponceDeleted(BaseModel):
    comment: CommentModelReturned
    detail: str = messages.COMMENT_SUCCESSFULLY_DELETED
