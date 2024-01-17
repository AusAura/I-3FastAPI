import cloudinary
import cloudinary.uploader

from fastapi import APIRouter, Depends, File, UploadFile, Query, HTTPException
from fastapi.openapi.models import Response

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.conf.config import config
from src.database.db import get_db
from src.database.models import User
from src.repositories import publications as repositories_publications
from src.services.auth import auth_service
from src.schemas.publications import PublicationCreate, PubImageSchema, PublicationResponse, CurrentImageSchema, \
    PublicationUpdate, UpdatedImageSchema, QrCodeImageSchema, PublicationUsersResponse, TransformationKey
from src.services.qr_code import generate_qr_code_byte
from src.utils.my_logger import logger
import src.messages as msg

router = APIRouter(prefix='/publication', tags=['publications'])

# TODO services for cloudinary in cls
cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
    secure=True
)


@router.post('/upload_image', status_code=status.HTTP_201_CREATED, response_model=CurrentImageSchema)
async def upload_image(file: UploadFile = File(), user: User = Depends(auth_service.get_current_user)):
    # TODO services for cloudinary
    r = cloudinary.uploader.upload(file.file, public_id=f'Temp/{user.email}', overwrite=True)

    current_image_url = cloudinary.CloudinaryImage(f'Temp/{user.email}') \
        .build_url(width=250, height=250, crop='fill', version=r.get('version'))

    logger.info(f'upload image(temp) from user: {user.email} url: {current_image_url}')
    return CurrentImageSchema(**{"current_img": current_image_url})


@router.get('/transform_image', status_code=status.HTTP_201_CREATED, response_model=UpdatedImageSchema,
            description="Transform image keys: left, right, filter")
async def transform_image(body: TransformationKey, user: User = Depends(auth_service.get_current_user),
                          img_service=None):
    # TODO services for cloudinary
    updated_image_url = img_service.transform_img(body.key, user.email)
    return UpdatedImageSchema(**{"updated_img": updated_image_url})


@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=PublicationResponse)
async def create_publication(body: PublicationCreate,
                             db: AsyncSession = Depends(get_db),
                             user: User = Depends(auth_service.get_current_user)):
    # TODO services for cloudinary
    current_image_url = cloudinary.CloudinaryImage(f'Temp/{user.email}').build_url()
    logger.info(f'get image(temp) from user : {user.email} url: {current_image_url}')
    img_body = PubImageSchema(**{"current_img": current_image_url, "updated_img": None, "qr_code_img": None})
    publication = await repositories_publications.create_publication(body, img_body, db, user)
    logger.info(f'User {user.email} create publication: {publication}')
    # TODO services for cloudinary delete temp image
    return publication


@router.get('/get_all_publications', status_code=status.HTTP_200_OK, response_model=list[PublicationUsersResponse])
async def get_publications(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                           db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    publications = await repositories_publications.get_all_publications(limit, offset, db)

    return publications


@router.get('/get_my_publications', status_code=status.HTTP_200_OK, response_model=list[PublicationResponse])
async def get_publications(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                           db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    publications = await repositories_publications.get_publications(limit, offset, db, user)

    if len(publications) == 0:
        logger.warning(f'User {user.email} try get not exist publications')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATIONS_EMPTY)

    logger.info(f'User {user.email} get count{len(publications)} publications')
    return publications


@router.get('/get/{publication_id}', status_code=status.HTTP_200_OK, response_model=PublicationResponse)
async def get_publication(publication_id: int, db: AsyncSession = Depends(get_db),
                          user: User = Depends(auth_service.get_current_user)):
    publication = await repositories_publications.get_publication(publication_id, db, user)

    if publication is None:
        logger.warning(f'User {user.email} try get not exist publication {publication_id}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)

    logger.info(f'User {user.email} get publication {publication_id}')
    return publication


@router.put('/update/{publication_id}', status_code=status.HTTP_200_OK, response_model=PublicationResponse)
async def update_text_publication(publication_id: int, body: PublicationUpdate,
                                  db: AsyncSession = Depends(get_db),
                                  user: User = Depends(auth_service.get_current_user)):
    publication = await repositories_publications.update_text_publication(publication_id, body, db, user)
    if publication is None:
        logger.warning(f'User {user.email} try update not exist publication {publication_id}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)

    logger.info(f'User {user.email} update publication {publication_id}')
    return publication


@router.delete('/delete/{publication_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_publication(publication_id: int, db: AsyncSession = Depends(get_db),
                             user: User = Depends(auth_service.get_current_user)):
    # TODO onecase delete image in table
    publication = await repositories_publications.delete_publication(publication_id, db, user)
    if publication is None:
        logger.warning(f'User {user.email} try delete not exist publication {publication_id}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)

    return publication


@router.post("/update_image/{publication_id}/{key}", status_code=status.HTTP_200_OK, response_model=UpdatedImageSchema)
async def update_image(publication_id: int, key: str, db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    # TODO services for cloudinary change image for KEY get url
    body = UpdatedImageSchema(updated_img=key)  # TODO url
    publication = await repositories_publications.update_image(publication_id, body, db, user)
    if publication is None:
        logger.warning(f'User {user.email} try update not exist publication {publication_id}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)

    logger.info(f'User {user.email} update image publication {publication_id}')
    # TODO response response_model / redirect ?
    return body


@router.get('/qr_code/{publication_id}', status_code=status.HTTP_200_OK, response_model=QrCodeImageSchema)
async def get_qr_code(publication_id: int, db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    publication = await repositories_publications.get_publication(publication_id, db, user)
    if publication is None:
        logger.warning(f'User {user.email} try get not exist publication {publication_id}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)

    img_bytes = await generate_qr_code_byte(publication.image.current_img)  # TODO udated_img

    cloudinary.uploader.upload(img_bytes, public_id=f'QrCode/{user.email}', overwrite=True)  # TODO in services
    qr_code_img = cloudinary.CloudinaryImage(f'QrCode/{user.email}').build_url()  # TODO in services

    qr_code_img = QrCodeImageSchema(qr_code_img=qr_code_img)
    await repositories_publications.update_image(publication_id, qr_code_img, db, user)
    return qr_code_img
