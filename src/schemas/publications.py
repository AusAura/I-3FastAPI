from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel, Field


class TempImage(BaseModel):
    current_img: str


class PubImageSchema(TempImage):
    updated_img: Optional[str] = None
    qr_code_img: Optional[str] = None


class PublicationSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    # tags: Optional[list[str]] = Field(None, max_items=5)  # TODO  Optional[list[Tag]]


class PublicationCreate(PublicationSchema):
    pass


class PublicationResponse(PublicationSchema):
    image: PubImageSchema

    class Config:
        from_attributes = True
