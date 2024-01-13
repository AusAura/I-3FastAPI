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

from src.database.db import get_db
from src.database.models import User
from src.schemas.user import UserResponse
from src.services.auth import auth_service
from src.conf.config import config
from src.repositories import users as repositories_users

router = APIRouter(prefix="/users", tags=["users"])
cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
    secure=True,
)


@router.get(
    "/me",
    response_model=UserResponse,
    )
async def read_user_me(user: User = Depends(auth_service.get_current_user)):
    return user

# TODO after Cloudinary
# @router.patch(
#     "/avatar",
#     response_model=UserResponse,
#     )
# async def get_current_user(
#     file: UploadFile = File(),
#     user: User = Depends(auth_service.get_current_user),
#     db: AsyncSession = Depends(get_db),
# ):
#     public_id = f"S2/{user.email}"
#     res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
#     print(res)
#     res_url = cloudinary.CloudinaryImage(public_id).build_url(
#         width=250, height=250, crop="fill", version=res.get("version")
#     )
#     user = await repositories_users.update_avatar_url(user.email, res_url, db)
#     auth_service.cache.set(user.email, pickle.dumps(user))
#     auth_service.cache.expire(user.email, 300)
#     return user
