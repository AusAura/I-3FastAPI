from pydantic import BaseModel, Field


class TagSchema(BaseModel):
    name: str = Field(min_length=3, max_length=15)


class TagsDetailResponse(BaseModel):
    detail: str
    tag: TagSchema
