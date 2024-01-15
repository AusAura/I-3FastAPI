from pydantic import BaseModel

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: str

class TagResponse(TagBase):
    id: int

    class Config:
        from_attributes = True

