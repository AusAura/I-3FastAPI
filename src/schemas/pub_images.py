from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator
from starlette import status

from src.services.cloud_in_ary.cloud_image import TRANSFORMATION_KEYS


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
    key: str = Field()

    @field_validator("key")
    def validate_key(cls, key: str) -> str:   # noqa
        if key not in TRANSFORMATION_KEYS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid transformation key: {key}")
        return key
