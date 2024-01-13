from typing import Optional

from pydantic import BaseModel, Field


class PubImageSchema(BaseModel):
    current_img: str
    updated_img: Optional[str] = None
    qr_code_img: Optional[str] = None


class PublicationSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    # tags: Optional[list[str]] = Field(None, max_items=5)  # TODO  Optional[list[Tag]]


class PublicationCreate(PublicationSchema):
    pass


class PublicationReturn(PublicationSchema):
    image: PubImageSchema
