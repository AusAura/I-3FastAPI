from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from src.database.models import Role


class UserNameSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)


class AboutSchema(BaseModel):
    about: Optional[str] = Field(None, min_length=1, max_length=255)


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(pattern=r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.-]+.[a-z]+$")
    password: str = Field(min_length=6, max_length=15)
    about: Optional[str] = Field(None, min_length=1, max_length=255)


class UserResponse(BaseModel):
    id: int = 1
    username: str = Field(min_length=3, max_length=50)
    email: str
    avatar: str
    about: Optional[str] = Field(None, min_length=1, max_length=255)
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
