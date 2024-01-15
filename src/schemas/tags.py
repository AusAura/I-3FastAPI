from pydantic import BaseModel, Field

class TagBase(BaseModel):
    name: str = Field(min_length=3, max_length=15)

class TagCreate(TagBase):
    pass

class TagUpdate(TagBase):
    pass

class TagPublication(TagBase):
    id: int

    class Config:
        from_attributes = True

