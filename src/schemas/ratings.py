from pydantic import BaseModel, Field


class RatingBase(BaseModel):
    score: int = Field(ge=1, le=5)


class RatingCreate(RatingBase):
    pass


class RatingUpdate(RatingBase):
    pass


class RatingResponse(RatingBase):
    pass
