import cloudinary
import cloudinary.uploader

from fastapi import APIRouter, Depends, File, UploadFile, Query

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.conf.config import config
from src.database.db import get_db
from src.database.models import User
from src.repositories import publications as repositories_publications
from src.services.auth import auth_service
from src.schemas.publications import PublicationCreate, PubImageSchema, PublicationResponse, TempImage
from src.utils.my_logger import logger

router = APIRouter(prefix='/publication', tags=['Publications'])

cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
    secure=True
)


@router.post('/upload_image', status_code=status.HTTP_201_CREATED, response_model=TempImage)
async def upload_image(file: UploadFile = File(), user: User = Depends(auth_service.get_current_user)):
    # TODO services for cloudinary
    r = cloudinary.uploader.upload(file.file, public_id=f'Temp/{user.email}', overwrite=True)

    current_image_url = cloudinary.CloudinaryImage(f'Temp/{user.email}') \
        .build_url(width=250, height=250, crop='fill', version=r.get('version'))

    return TempImage(**{"current_img": current_image_url})


@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=PublicationResponse)
async def create_publication(body: PublicationCreate,
                             db: AsyncSession = Depends(get_db),
                             user: User = Depends(auth_service.get_current_user)):
    # TODO services for cloudinary
    current_image_url = cloudinary.CloudinaryImage(f'Temp/{user.email}').build_url()
    img_body = PubImageSchema(**{"current_img": current_image_url, "updated_img": None, "qr_code_img": None})
    publication = await repositories_publications.create_publication(body, img_body, db, user)
    # TODO services for cloudinary delete temp image
    return publication


@router.get('/', response_model=list[PublicationResponse])
async def get_publications(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                           db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):

    publications = await repositories_publications.get_publications(limit, offset, db, user)
    return publications
