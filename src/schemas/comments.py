from datetime import datetime, date
from pydantic import BaseModel, Field, EmailStr

from src.schemas import comments


class CommentModel(BaseModel):
    id: int
    username: str
    text: str
    publication_id: int

    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class CommentResponceAdded(BaseModel):
    comment: CommentModel
    detail: str = comments.CommentResponceAdded

class CommentResponceEdited(BaseModel):
    comment: CommentModel
    detail: str = comments.CommentResponceEdited

class CommentResponceDeleted(BaseModel):
    comment: CommentModel
    detail: str = comments.CommentResponceDeleted
