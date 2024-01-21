from fastapi import APIRouter, Depends, File, UploadFile, Query, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.database.db import get_db
from src.database.models import User, Role, Publication
from src.repositories import publications as repositories_publications
from src.repositories import users as repository_users

from src.schemas.publications import PublicationCreate, PublicationResponse, PublicationUpdate, PublicationUsersResponse, \
    PublicationCreateAdmin, PublicationUpdateAdmin

from src.schemas.publications import PublicationCreate, PublicationResponse, PublicationUpdate
from src.schemas.pub_images import PubImageSchema, CurrentImageSchema, UpdatedImageSchema, QrCodeImageSchema, \
    TransformationKey

from src.services.qr_code import generate_qr_code_byte
from src.services.auth import auth_service
from src.services.cloud_in_ary.cloud_image import cloud_img_service, CloudinaryService, TRANSFORMATION_KEYS
from src.services.cloud_in_ary.errors import CloudinaryResourceNotFoundError, CloudinaryLoadingError

from src.utils.my_logger import logger
import src.messages as msg

router = APIRouter(prefix='/publications', tags=['publications'])


## Utilitary?
@router.post('/upload_image', status_code=status.HTTP_201_CREATED, response_model=CurrentImageSchema)
async def upload_image(file: UploadFile = File(), user: User = Depends(auth_service.get_current_user),
                       cloud: CloudinaryService = Depends(cloud_img_service)):
    """
    Upload image

    Load image from user and save it in Cloudinary
    folder {email}/temp/ with postfix current_img
    :param file: UploadFile
    :param user: current user owner of image in Cloudinary folder {email}/temp/
    :param cloud: object CloudinaryService
    :return: CurrentImageSchema with url
    """
    current_image_url = cloud.save_by_email(file.file, user.email, "current_img", None, 'temp')

    logger.info(f'upload image(temp) from user: {user.email} url: {current_image_url}')

    return CurrentImageSchema(**{"current_img": current_image_url})


## Utilitary?
@router.post('/transform_image', status_code=status.HTTP_201_CREATED, response_model=UpdatedImageSchema,
             description=f"Transform image keys : {', '.join(TRANSFORMATION_KEYS)}")
async def transform_image(body: TransformationKey, user: User = Depends(auth_service.get_current_user),
                          cloud: CloudinaryService = Depends(cloud_img_service)):
    """
    Transform image

    Update current image by key and save it in Cloudinary folder {email}/temp/ with postfix updated_img
    changed image will be stacked, by use this router over and over
    :param body: TransformationKey
    :param user: current user owner of image in Cloudinary folder {email}/temp/
    :param cloud: object CloudinaryService
    :return: UpdatedImageSchema with url
    :raises HTTPException: 400 in pydentic schema if key not in TRANSFORMATION_KEYS (list of available keys)
    :raises HTTPException: 400 if image not uploaded in {email}/temp/ by postfix current_img (base img)
    """
    try:
        updated_image_url = cloud.apply_transformation(
            key=body.key, email=user.email,
            current_postfix="current_img", updated_postfix="updated_img"
        )
    except CloudinaryResourceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PLEASE_UPLOAD_IMAGE)
    except CloudinaryLoadingError:
        # status ??
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg.CLOUDINARY_LOADING_ERROR)

    return UpdatedImageSchema(**{"updated_img": updated_image_url})


## user/admin, created by anyone, admin creates empty-imaged publication
@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=PublicationResponse)
async def create_publication(body: PublicationCreate, db: AsyncSession = Depends(get_db),
                             user: User = Depends(auth_service.get_current_user),
                             cloud: CloudinaryService = Depends(cloud_img_service)):
    """
    Create publication

    Create publication with current_img(must be uploaded) and updated_img(optional) in Cloudinary
    :param body: title, description
    :param db: AsyncSession
    :param user: current user (creator) owner of publication
    :param cloud: object CloudinaryService
    :return: publication by PublicationResponse (title, description, image)
    :raises HTTPException: 400 if image not uploaded in {email}/temp/ by postfix current_img (base img)
    """
    
    email = user.email

    # check base image on existence in path {email}/temp/current_img
    if cloud.get_cloud_id(email, "current_img") is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg.PLEASE_UPLOAD_IMAGE)

    # create publication with empty PubImage, rel one_to_one in field publication.image
    img_body = PubImageSchema(**{"current_img": "костыль", "updated_img": None, "qr_code_img": None})
    publication = await repositories_publications.create_publication(body, img_body, db, user)

    # replace temp images to folder {email}/publications/{publication_id}/postfix_name & create schemas
    current_image_body = CurrentImageSchema(**cloud.replace_temp_to_publications(
        email=email,
        postfix="current_img",
        post_id=publication.id))
    # if None - save None in publication.image.updated_img
    update_image_body = UpdatedImageSchema(**cloud.replace_temp_to_publications(
        email=email,
        postfix="updated_img",
        post_id=publication.id))

    # save images to database with in table PubImage, rel one_to_one in field publication.image
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
@router.get('/all_my', status_code=status.HTTP_200_OK, response_model=list[PublicationResponse])
async def get_publications(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                           db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Get all publications of current user
    :param limit:
    :param offset:
    :param db: AsyncSession
    :param user: current user owner of publications
    :return: publications list with PublicationResponse (title, description, image)
    :raises HTTPException: 404 if publications not exist
    """

    logger_actor = user.email + f"({user.role})"
    publications = await repositories_publications.get_publications(limit, offset, db, user)

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
@router.get('/{publication_id}', status_code=status.HTTP_200_OK, response_model=PublicationResponse)
async def get_publication(publication_id: int, db: AsyncSession = Depends(get_db),
                          user: User = Depends(auth_service.get_current_user)):
    """
    Get publication by id
    :param publication_id:
    :param db: AsyncSession
    :param user: current user owner of publication
    :return: publication by PublicationResponse (title, description, image)
    :raises HTTPException: 404 if publication not exist or user not owner
    """
    
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
@router.put('/{publication_id}/update_text', status_code=status.HTTP_200_OK, response_model=PublicationResponse)
async def update_text_publication(publication_id: int, body: PublicationUpdate,
                                  db: AsyncSession = Depends(get_db),
                                  user: User = Depends(auth_service.get_current_user)):
    """
    Update publication text (title, description)
    :param publication_id:
    :param body: title(str), description(str)
    :param db: AsyncSession
    :param user: current user owner of publication
    :return: publication by PublicationResponse (title, description, image)
    :raises HTTPException: 404 if publication not exist or user not owner
    """
    
    logger_actor = user.email + f'({user.role})'

    if user.role == Role.admin:
        user = await repository_users.get_user_by_publication_id(publication_id, db)

    publication = await repositories_publications.update_text_publication(publication_id, body, db, user)
    if publication is None:
        logger.warning(f'User {logger_actor} try update not exist publication {publication_id}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)

    logger.info(f'User {logger_actor} update publication {publication_id}')
    return publication


## Admin/User, 1 publication
@router.put("/{publication_id}/update_image", status_code=status.HTTP_200_OK, response_model=UpdatedImageSchema,
            description=f"Transform image keys : {', '.join(TRANSFORMATION_KEYS)}")
async def update_image(publication_id: int, body: TransformationKey, db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user),
                       cloud: CloudinaryService = Depends(cloud_img_service)):
    """
    Update publication image

    Get publication by id and use transformation keys to upload new transformed image
    in cloudinary also save in database Cloudinary url the last of new image
    :param publication_id:
    :param body: key(str) in TRANSFORMATION_KEYS
    :param db: AsyncSession
    :param user: current user owner of publication
    :param cloud: object CloudinaryService
    :return: UpdatedImageSchema with url the last of new image
    :raises HTTPException: 404 if publication not exist or user not owner
    :raises HTTPException: 400 if key not in TRANSFORMATION_KEYS
    :raises HTTPException: if image not exist in cloudinary {email}/publications/{publication_id}/current_img
    """
    
    publication = await repositories_publications.get_publication(publication_id, db, user)
      
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

    # apply transformation by key in cloud path {email}/publications/{publication_id}/postfix_name
    # if exist updated_img in cloud apply transformation to it
    # else apply to current_img and save like updated_img
    try:
        updated_image_url = cloud.apply_transformation(
            key=body.key, email=user.email, folder="publications", post_id=publication_id,
            current_postfix="current_img", updated_postfix="updated_img"
        )
    except CloudinaryResourceNotFoundError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg.PLEASE_UPLOAD_IMAGE)
    except CloudinaryLoadingError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg.CLOUDINARY_LOADING_ERROR)

    # update image in database with url the last of new image to publication.image.updated_img
    update_image_body = UpdatedImageSchema(**{"updated_img": updated_image_url})
    await repositories_publications.update_image(publication_id, update_image_body, db, user)

    return update_image_body


@router.get('/{publication_id}/qr_code', status_code=status.HTTP_200_OK, response_model=QrCodeImageSchema)
async def get_qr_code(publication_id: int, db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user),
                      cloud: CloudinaryService = Depends(cloud_img_service)):
  
    """
    Get qr code image from database and save in cloudinary
    folder {email}/publications/{publication_id}/qr_code_img also save in database qr code cloud url
    :param publication_id:
    :param db: AsyncSession
    :param user: current user owner of publication
    :param cloud: object CloudinaryService
    :return: QrCodeImageSchema with qr code cloud url
    :raises HTTPException: 404 if publication not exist or user not owner
    """
    
    logger_actor = user.email + f'({user.role})'
    if user.role == Role.admin:
        user = await repository_users.get_user_by_publication_id(publication_id, db)

    publication = await repositories_publications.get_publication(publication_id, db, user)
    if publication is None:
        logger.warning(f'User {logger_actor} try get not exist publication {publication_id}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)

    # get cloud url in database updated_img if exist else current_img
    img_url = publication.image.updated_img if publication.image.updated_img is not None else publication.image.current_img
    img_bytes = await generate_qr_code_byte(img_url)
    # save in cloudinary folder {email}/publications/{post_id}/qr_code_img
    qr_code_url = cloud.save_by_email(img_bytes, user.email, post_id=publication_id, folder="publications",
                                      postfix="qr_code_img")
    # update in database qr code cloud url to publication.image.qr_code_img
    qr_code_img_body = QrCodeImageSchema(qr_code_img=qr_code_url)
    await repositories_publications.update_image(publication_id, qr_code_img_body, db, user)
    return qr_code_img_body

  
## Admin/User, 1 user by publication id
@router.delete('/{publication_id}/delete', status_code=status.HTTP_204_NO_CONTENT)
async def delete_publication(publication_id: int, db: AsyncSession = Depends(get_db),
                             user: User = Depends(auth_service.get_current_user),
                             cloud: CloudinaryService = Depends(cloud_img_service)):
    """
    Delete publication from database and cloudinary images and folder
    also delete images(PubImage) in database cascade='all,delete' (one to one)
    :param publication_id:
    :param db: AsyncSession
    :param user: current user owner of publication
    :param cloud: object CloudinaryService
    :return: None
    :raises HTTPException: 404 if publication not exist or user not owner
    """
    
    email = user.email  # user email here because missing Greenlet
    logger_actor = user.email + f'({user.role})'

    if user.role == Role.admin:
        user = await repository_users.get_user_by_publication_id(publication_id, db)

    publication = await repositories_publications.delete_publication(publication_id, db, user)
    
    if publication is None:
        logger.warning(f'User {logger_actor} try delete not exist publication {publication_id}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg.PUBLICATION_NOT_FOUND)
        
    # delete images in cloudinary folder {email}/publications/{publication_id} and delete folder {publication_id}
    cloud.delete_by_email(email, publication_id, folder="publications",
                          postfixes=["current_img", "updated_img", "qr_code_img"])
    
    return publication  
 