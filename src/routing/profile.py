import pickle

import cloudinary
import cloudinary.uploader
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Path,
    Query,
    UploadFile,
    File,
)
# from fastapi_limiter.depends import
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.database.db import get_db
from src.database.models import User
from src.messages import USER_NOT_FOUND, USER_ALREADY_EXISTS
from src.schemas.user import UserProfile, UserResponse
from src.services.auth import auth_service
from src.conf.config import config
from src.repositories import users as repositories_users

router = APIRouter(prefix="/profile", tags=["profile"])
cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
    secure=True,
)


@router.get("/{username}", response_model=UserProfile)
async def read_user_profile(username: str, db: AsyncSession = Depends(get_db)):
    user = await repositories_users.get_user_by_username(username, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND)
    quantity_publications = await repositories_users.count_user_publications(user.id, db)
    usage_days = await repositories_users.calculate_usage_days(user.created_at)

    return {"user": user, "publications_count": quantity_publications, "usage_days": usage_days}


@router.patch("/{new_username}/change_username", response_model=UserResponse)
async def change_username(new_username: str,
                          user: User = Depends(auth_service.get_current_user),
                          db: AsyncSession = Depends(get_db),
                          ):
    try:
        user = await repositories_users.update_username(user, new_username, db)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=USER_ALREADY_EXISTS)
    return user


@router.patch("/change_avatar", response_model=UserResponse)
async def get_current_user(
    file: UploadFile = File(),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    public_id = f"avatar {user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)

    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repositories_users.update_avatar_url(user.email, res_url, db)

    return user
