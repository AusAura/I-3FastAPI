import pickle

import cloudinary
import cloudinary.uploader

from fastapi import APIRouter, Depends, UploadFile, File
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.conf.config import config
from src.database.db import get_db
from src.database.models import User
from src.dependency import get_cache
from src.repositories import publications as repositories_publications
from src.schemas.publications import PublicationCreate, PublicationNoImg, PubImageSchema

router = APIRouter(prefix='/publication', tags=['Publications'])

cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
    secure=True
)


# TODO START zaglushka
class auth_service:
    def get_current_user(self):
        return User(id=1, username="test", email="test@test.com")


# TODO END zaglushka


@router.post('/upload_image', status_code=status.HTTP_201_CREATED)
async def upload_image(user: User, file: UploadFile = File()):
    r = cloudinary.uploader.upload(file.file, public_id=f'NotesApp/{user.email}', overwrite=True)
    current_image_url = cloudinary.CloudinaryImage(f'NotesApp/{user.email}') \
        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    return current_image_url


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_publication(body: PublicationNoImg, db: AsyncSession = Depends(get_db),
                             user: User = Depends(auth_service.get_current_user),
                             uploader=Depends(upload_image)):

    current_image_url = await uploader(user)
    # TODO some changes with cloudinary
    create_body = PublicationCreate(**body.model_dump(exclude_unset=True),
                                    image=PubImageSchema(current_img=current_image_url))
    publication = repositories_publications.create_publication(create_body, db, user)

    return publication


