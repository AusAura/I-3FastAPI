from fastapi import APIRouter, Depends, File, UploadFile, Query, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.database.db import get_db
from src.database.models import User
from src.repositories import publications as repositories_publications

from src.schemas.publications import PublicationCreate, PublicationResponse, PublicationUpdate, PublicationUsersResponse
from src.schemas.pub_images import PubImageSchema, CurrentImageSchema, UpdatedImageSchema, QrCodeImageSchema, \
    TransformationKey

from src.services.qr_code import generate_qr_code_byte
from src.services.auth import auth_service
from src.services.cloud_image import cloud_img_service, CloudinaryService

from src.utils.my_logger import logger
import src.messages as msg

router = APIRouter(prefix='/publications', tags=['publications'])


@router.post('/upload_image', status_code=status.HTTP_201_CREATED, response_model=CurrentImageSchema)
async def upload_image(file: UploadFile = File(), user: User = Depends(auth_service.get_current_user),
                       cloud: CloudinaryService = Depends(cloud_img_service)):
    current_image_url = cloud.save_by_email(file.file, user.email, "current_img", None, 'temp')

    logger.info(f'upload image(temp) from user: {user.email} url: {current_image_url}')

    return CurrentImageSchema(**{"current_img": current_image_url})


@router.put('/transform_image', status_code=status.HTTP_201_CREATED, response_model=UpdatedImageSchema,
            description="Transform image keys")
async def transform_image(body: TransformationKey, user: User = Depends(auth_service.get_current_user),
                          cloud: CloudinaryService = Depends(cloud_img_service)):

    # TODO может єту логику лучше убрать внутрь класса ? или оставить тут?
    if (cloud_id := cloud.get_cloud_id(email=user.email, postfix="updated_img")) is None:
        cloud_id = cloud.get_cloud_id(email=user.email, postfix="current_img")
        if cloud_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg.PLEASE_UPLOAD_IMAGE)

    updated_image_url = cloud.apply_transformation(key=body.key, cloud_id=cloud_id)

    return UpdatedImageSchema(**{"updated_img": updated_image_url})


@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=PublicationResponse)
async def create_publication(body: PublicationCreate, db: AsyncSession = Depends(get_db),
                             user: User = Depends(auth_service.get_current_user),
                             cloud: CloudinaryService = Depends(cloud_img_service)):

    if cloud.get_cloud_id(user.email, "current_img") is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg.PLEASE_UPLOAD_IMAGE)

    img_body = PubImageSchema(**{"current_img": "костыль", "updated_img": None, "qr_code_img": None})
    publication = await repositories_publications.create_publication(body, img_body, db, user)

    current_image_body = CurrentImageSchema(**cloud.replace_temp_to_publications(
        email=user.email,
        postfix="current_img",
        post_id=publication.id))

    update_image_body = UpdatedImageSchema(**cloud.replace_temp_to_publications(
        email=user.email,
        postfix="updated_img",
        post_id=publication.id))

    publication = await repositories_publications.update_image(publication.id, current_image_body, db, user)
    publication = await repositories_publications.update_image(publication.id, update_image_body, db, user)

    return publication


@router.get('/all', status_code=status.HTTP_200_OK, response_model=list[PublicationUsersResponse])
async def get_publications(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                           db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    publications = await repositories_publications.get_all_publications(limit, offset, db)

    return publications


@router.get('/all_my', status_code=status.HTTP_200_OK, response_model=list[PublicationResponse])
async def get_publications(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                           db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    publications = await repositories_publications.get_publications(limit, offset, db, user)

    if len(publications) == 0:
        logger.warning(f'User {user.email} try get not exist publications')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATIONS_EMPTY)

    logger.info(f'User {user.email} get count{len(publications)} publications')
    return publications


@router.get('/{publication_id}', status_code=status.HTTP_200_OK, response_model=PublicationResponse)
async def get_publication(publication_id: int, db: AsyncSession = Depends(get_db),
                          user: User = Depends(auth_service.get_current_user)):
    publication = await repositories_publications.get_publication(publication_id, db, user)

    if publication is None:
        logger.warning(f'User {user.email} try get not exist publication {publication_id}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)

    logger.info(f'User {user.email} get publication {publication_id}')
    return publication


@router.put('/{publication_id}/update_text', status_code=status.HTTP_200_OK, response_model=PublicationResponse)
async def update_text_publication(publication_id: int, body: PublicationUpdate,
                                  db: AsyncSession = Depends(get_db),
                                  user: User = Depends(auth_service.get_current_user)):
    publication = await repositories_publications.update_text_publication(publication_id, body, db, user)
    if publication is None:
        logger.warning(f'User {user.email} try update not exist publication {publication_id}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)

    logger.info(f'User {user.email} update publication {publication_id}')
    return publication


@router.delete('/{publication_id}/delete', status_code=status.HTTP_204_NO_CONTENT)
async def delete_publication(publication_id: int, db: AsyncSession = Depends(get_db),
                             user: User = Depends(auth_service.get_current_user)):
    # TODO onecase delete image in table
    publication = await repositories_publications.delete_publication(publication_id, db, user)
    if publication is None:
        logger.warning(f'User {user.email} try delete not exist publication {publication_id}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)
    # TODO delete image in cloud
    return publication


@router.post("/{publication_id}/update_image/{key}", status_code=status.HTTP_200_OK, response_model=UpdatedImageSchema)
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


@router.get('/{publication_id}/qr_code', status_code=status.HTTP_200_OK, response_model=QrCodeImageSchema)
async def get_qr_code(publication_id: int, db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user),
                      cloud: CloudinaryService = Depends(cloud_img_service)):

    publication = await repositories_publications.get_publication(publication_id, db, user)
    if publication is None:
        logger.warning(f'User {user.email} try get not exist publication {publication_id}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)

    img_url = publication.image.updated_img if publication.image.updated_img is not None else publication.image.current_img
    img_bytes = await generate_qr_code_byte(img_url)
    qr_code_url = cloud.save_by_email(img_bytes, user.email, post_id=publication_id, folder="publications", postfix="qr_code_img")

    qr_code_img = QrCodeImageSchema(qr_code_img=qr_code_url)
    await repositories_publications.update_image(publication_id, qr_code_img, db, user)
    return qr_code_img
