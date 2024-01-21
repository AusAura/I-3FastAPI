from fastapi import APIRouter, Depends, File, UploadFile, Query, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.database.db import get_db
from src.database.models import User, Role, Publication
from src.repositories import publications as repositories_publications
from src.repositories import users as repository_users

from src.schemas.publications import PublicationCreate, PublicationResponse, PublicationUpdate, PublicationUsersResponse, \
    PublicationCreateAdmin, PublicationUpdateAdmin

from src.schemas.pub_images import PubImageSchema, CurrentImageSchema, UpdatedImageSchema, QrCodeImageSchema, \
    TransformationKey, BaseImageSchema

from src.services.qr_code import generate_qr_code_byte
from src.services.auth import auth_service
from src.services.cloud_image import cloud_img_service, CloudinaryService

from src.utils.my_logger import logger
import src.messages as msg

router = APIRouter(prefix='/publication', tags=['publications'])


## Utilitary?
@router.post('/upload_image', status_code=status.HTTP_201_CREATED, response_model=CurrentImageSchema)
async def upload_image(file: UploadFile = File(), user: User = Depends(auth_service.get_current_user),
                       cloud: CloudinaryService = Depends(cloud_img_service)):
    
    current_image_url = cloud.save_by_email(file.file, user.email, "current_img", None, 'temp')

    logger.info(f'upload image(temp) from user: {user.email} url: {current_image_url}')

    return CurrentImageSchema(**{"current_img": current_image_url})


## Utilitary?
@router.get('/transform_image', status_code=status.HTTP_201_CREATED, response_model=UpdatedImageSchema,
            description="Transform image keys: left, right, filter")
async def transform_image(body: TransformationKey, user: User = Depends(auth_service.get_current_user),
                          img_service=None):
    # TODO services for cloudinary
    updated_image_url = img_service.transform_img(body.key, user.email)
    return UpdatedImageSchema(**{"updated_img": updated_image_url})


## user/admin, created by anyone, admin creates empty-imaged publication
@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=PublicationResponse)
async def create_publication(body: PublicationCreate, db: AsyncSession = Depends(get_db),
                             user: User = Depends(auth_service.get_current_user),
                             cloud: CloudinaryService = Depends(cloud_img_service),
                             ):

    email = user.email

    img_body = PubImageSchema(**{"current_img": "костыль", "updated_img": None, "qr_code_img": None})
    publication = await repositories_publications.create_publication(body, img_body, db, user)

    if not cloud.image_exists(email, "current_img"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg.PLEASE_UPLOAD_IMAGE)

    current_image_body = CurrentImageSchema(**cloud.replace_temp_to_publications(
        email=email,
        postfix="current_img",
        post_id=publication.id))

    update_image_body = UpdatedImageSchema(**cloud.replace_temp_to_publications(
        email=email,
        postfix="updated_img",
        post_id=publication.id))

    publication = await repositories_publications.update_image(publication.id, current_image_body, db, user)
    publication = await repositories_publications.update_image(publication.id, update_image_body, db, user)

    return publication


# User/Admin, every publication
@router.get('/get_all_publications', status_code=status.HTTP_200_OK, response_model=list[PublicationUsersResponse])
async def get_all_publications(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                           db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    publications = await repositories_publications.get_all_publications(limit, offset, db)

    return publications


# User-only, for current user
@router.get('/get_my_publications', status_code=status.HTTP_200_OK, response_model=list[PublicationResponse])
async def get_user_publications(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                           db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    
    logger_actor = user.email + f"({user.role})"

    publications = await repositories_publications.get_user_publications(limit, offset, db, user)

    if len(publications) == 0:
        logger.warning(f'User {logger_actor} try get not exist publications')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATIONS_EMPTY)

    logger.info(f'User {logger_actor} get count{len(publications)} publications')
    return publications


#Admin-only, for 1 user
@router.get('/get_user_publications/{user_id}', status_code=status.HTTP_200_OK, response_model=list[PublicationResponse])
async def get_user_publications(user_id: int, limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                           db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    
    logger_actor = user.email + f"({user.role})"

    if user.role == Role.admin:
        user = await repository_users.get_user_by_id(user_id, db)

        if user is None:
            logger.warning(f'User {logger_actor} try get not exist user {user_id}')
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.USER_NOT_FOUND)   

        publications = await repositories_publications.get_user_publications(limit, offset, db, user)

        if len(publications) == 0:
            logger.warning(f'User {logger_actor} try get not exist publications')
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATIONS_EMPTY)
        
        logger.info(f'User {logger_actor} get count{len(publications)} publications')
        return publications
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg.FORBIDDEN)



## Admin/User, get 1 publication
@router.get('/get/{publication_id}', status_code=status.HTTP_200_OK, response_model=PublicationResponse)
async def get_publication(publication_id: int, db: AsyncSession = Depends(get_db),
                          user: User = Depends(auth_service.get_current_user)):
    
    logger_actor = user.email + f"({user.role})"
    if user.role == Role.admin:
        user = await repository_users.get_user_by_publication_id(publication_id, db)

    publication = await repositories_publications.get_publication(publication_id, db, user)

    if publication is None:
        logger.warning(f'User {logger_actor} try get not exist publication {publication_id}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)

    logger.info(f'User {logger_actor} get publication {publication_id}')
    return publication


## Admin/User, 1 user by publication id
@router.put('/update/{publication_id}', status_code=status.HTTP_200_OK, response_model=PublicationResponse)
async def update_text_publication(publication_id: int, body: PublicationUpdate,
                                  db: AsyncSession = Depends(get_db),
                                  user: User = Depends(auth_service.get_current_user)):
    
    logger_actor = user.email + f'({user.role})'

    if user.role == Role.admin:
        user = await repository_users.get_user_by_publication_id(publication_id, db)

    publication = await repositories_publications.update_text_publication(publication_id, body, db, user)
    if publication is None:
        logger.warning(f'User {logger_actor} try update not exist publication {publication_id}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)

    logger.info(f'User {logger_actor} update publication {publication_id}')
    return publication


## Admin/User, 1 user by publication id
@router.delete('/delete/{publication_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_publication(publication_id: int, db: AsyncSession = Depends(get_db),
                             user: User = Depends(auth_service.get_current_user)):
    
    logger_actor = user.email + f'({user.role})'

    if user.role == Role.admin:
        user = await repository_users.get_user_by_publication_id(publication_id, db)

    # TODO onecase delete image in table
    publication = await repositories_publications.delete_publication(publication_id, db, user)
    if publication is None:
        logger.warning(f'User {logger_actor} try delete not exist publication {publication_id}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)
    # TODO delete image in cloud
    return publication


## Admin/User, 1 publication
@router.post("/update_image/{publication_id}/{key}", status_code=status.HTTP_200_OK, response_model=UpdatedImageSchema)
async def update_image(publication_id: int, key: str, db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
      
    logger_actor = user.email + f'({user.role})'

    if user.role == Role.admin:
        user = await repository_users.get_user_by_publication_id(publication_id, db)

    # TODO services for cloudinary change image for KEY get url
    body = UpdatedImageSchema(updated_img=key)  # TODO url
    publication = await repositories_publications.update_image(publication_id, body, db, user)
    if publication is None:
        logger.warning(f'User {logger_actor} try update not exist publication {publication_id}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)

    logger.info(f'User {logger_actor} update image publication {publication_id}')
    # TODO response response_model / redirect ?
    return body


@router.get('/qr_code/{publication_id}', status_code=status.HTTP_200_OK, response_model=QrCodeImageSchema)
async def get_qr_code(publication_id: int, db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user),
                      cloud: CloudinaryService = Depends(cloud_img_service)):
    
    logger_actor = user.email + f'({user.role})'

    if user.role == Role.admin:
        user = await repository_users.get_user_by_publication_id(publication_id, db)


    publication = await repositories_publications.get_publication(publication_id, db, user)
    if publication is None:
        logger.warning(f'User {logger_actor} try get not exist publication {publication_id}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)

    img_url = publication.image.updated_img if publication.image.updated_img is not None else publication.image.current_img
    img_bytes = await generate_qr_code_byte(img_url)
    qr_code_url = cloud.save_by_email(img_bytes, logger_actor, post_id=publication_id, folder="publications", postfix="qr_code_img")

    qr_code_img = QrCodeImageSchema(qr_code_img=qr_code_url)
    await repositories_publications.update_image(publication_id, qr_code_img, db, user)
    return qr_code_img
