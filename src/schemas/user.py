from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from src.database.models import Role


class UserNameSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)


class AboutSchema(BaseModel):
    about: str = Field(min_length=6, max_length=500)


class UserSchema(BaseModel):
    username: UserNameSchema
    email: EmailStr = Field(pattern=r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.-]+.[a-z]+$")
    password: str = Field(min_length=6, max_length=15)
    about: AboutSchema


class UserResponse(BaseModel):
    id: int = 1
    username: str
    email: str
    avatar: str
    about: str | None
    role: Role

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    user: UserResponse
    publications_count: int
    usage_days: int

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: str
