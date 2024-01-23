import cloudinary
import cloudinary.uploader
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    UploadFile,
    File,
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.database.db import get_db
from src.database.models import User
from src.messages import USER_NOT_FOUND, USER_ALREADY_EXISTS
from src.schemas.user import UserProfile, UserResponse, UserNameSchema, AboutSchema
from src.services.auth import auth_service
from src.conf.config import config
from src.repositories import profile as repositories_profile
from src.services.cloud_in_ary.cloud_image import CloudinaryService, cloud_img_service

router = APIRouter(prefix="/profile", tags=["profile"])
cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
    secure=True,
)


@router.get("/{username}", response_model=UserProfile)
async def read_user_profile(username: str, db: AsyncSession = Depends(get_db)):
    user = await repositories_profile.get_user_by_username(username, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND)
    quantity_publications = await repositories_profile.count_user_publications(user.id, db)
    usage_days = await repositories_profile.count_usage_days(user.created_at, db)

    return {"user": user, "publications_count": quantity_publications, "usage_days": usage_days}


@router.patch("/change_username", response_model=UserResponse)
async def change_username(body: UserNameSchema,
                          user: User = Depends(auth_service.get_current_user),
                          db: AsyncSession = Depends(get_db),
                          ):
    try:
        user = await repositories_profile.update_username(user, body, db)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=USER_ALREADY_EXISTS)
    return user


@router.patch("/change_about", response_model=UserResponse)
async def change_about(body: AboutSchema,
                       user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_db),
                       ):
    user = await repositories_profile.update_about(user, body, db)
    return user


@router.patch("/change_avatar", response_model=UserResponse)
async def change_avatar(file: UploadFile = File(), user: User = Depends(auth_service.get_current_user),
                        db: AsyncSession = Depends(get_db), cloud: CloudinaryService = Depends(cloud_img_service)):
    avatar_url = cloud.save_by_email(file.file, user.email, "avatar", None, 'avatar')

    user = await repositories_profile.update_avatar_url(user.email, avatar_url, db)

    return user
