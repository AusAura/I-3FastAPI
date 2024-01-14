

from pydantic import BaseModel
# TODO refactor
class TagBase(BaseModel):
    name: str # присобачить к моим схемам

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True


