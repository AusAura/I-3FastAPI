from typing import Optional

from pydantic import BaseModel, Field

from src.schemas.pub_images import PubImageSchema
from src.schemas.user import UserResponse


class PublicationSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    # tags: Optional[list[str]] = Field(None, max_items=5)  # TODO  Optional[list[Tag]]


class PublicationCreate(PublicationSchema):
    pass


class PublicationUpdate(PublicationSchema):
    pass


class PublicationResponse(PublicationSchema):
    id: int
    image: PubImageSchema


class PublicationUsersResponse(PublicationResponse):
    user: UserResponse

    class Config:
        from_attributes = True
