from typing import Optional

from pydantic import BaseModel, Field, validator, field_validator

from src.schemas.user import UserResponse


class BaseImageSchema(BaseModel):
    pass


class CurrentImageSchema(BaseImageSchema):
    current_img: Optional[str] = None


class UpdatedImageSchema(BaseImageSchema):
    updated_img: Optional[str] = None


class QrCodeImageSchema(BaseImageSchema):
    qr_code_img: Optional[str] = None


class PubImageSchema(CurrentImageSchema, UpdatedImageSchema, QrCodeImageSchema):
    pass


class TransformationKey(BaseModel):
    key: str = Field(enum=["left", "right", "filter"])

    @field_validator("key")
    def validate_key(self, key: str) -> str:
        if key not in ["left", "right", "filter"]:
            raise ValueError(f"Invalid transformation key: {key}")
        return key


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
