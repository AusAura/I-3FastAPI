from typing import Optional

from pydantic import BaseModel, Field
from src.schemas.tags import TagSchema

from src.schemas.pub_images import PubImageSchema
from src.schemas.user import UserResponse


class PublicationSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, min_length=1, max_length=255)


class PublicationCreate(PublicationSchema):
    tags: Optional[list[TagSchema]] = Field(None, max_items=5)


class PublicationCreateAdmin(PublicationCreate):
    admin: dict


class PublicationUpdate(PublicationSchema):
    pass


class PublicationUpdateAdmin(PublicationUpdate):
    admin: dict


class PublicationResponse(PublicationSchema):
    id: int
    image: PubImageSchema
    tags_name: str
    average_rating: Optional[float]

    class Config:
        from_attributes = True


class PublicationResponseDetail(BaseModel):
    publication: PublicationResponse
    detail: str


class PublicationUsersResponse(PublicationResponse):
    user: UserResponse

    class Config:
        from_attributes = True
