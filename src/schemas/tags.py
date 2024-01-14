from typing import List

from pydantic import BaseModel

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True

class PublicationTag(TagBase):
    pass

class PublicationTagCreate(TagCreate):
    pass

class PublicationTag(Tag):
    pass
