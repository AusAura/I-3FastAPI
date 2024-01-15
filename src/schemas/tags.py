from pydantic import BaseModel

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: str

class TagPublication(TagBase):
    id: int

    class Config:
        from_attributes = True

