from typing import Optional

from pydantic import BaseModel, Field
from src.schemas.tags import TagPublication


class TempImage(BaseModel):
    current_img: str


class PubImageSchema(TempImage):
    updated_img: Optional[str] = None
    qr_code_img: Optional[str] = None


class PublicationSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    tags: Optional[list['TagPublication']] = Field(None, max_items=5)


class PublicationCreate(PublicationSchema):
    pass


class PublicationUpdate(PublicationSchema):
    pass


class PublicationResponse(PublicationSchema):
    image: PubImageSchema

    class Config:
        from_attributes = True
