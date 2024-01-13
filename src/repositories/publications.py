from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Publication, PubImage
from src.schemas.publications import PublicationCreate, PubImageSchema
from src.utils.my_logger import logger


async def create_pub_img(img_body: PubImageSchema, db: AsyncSession):
    pub_img = PubImage(**img_body.model_dump(exclude_unset=True))
    db.add(pub_img)
    await db.commit()
    await db.refresh(pub_img)
    return pub_img


async def create_publication(body: PublicationCreate, img_body: PubImageSchema, db: AsyncSession, user_id: int):

    pub_img = await create_pub_img(img_body, db)

    logger.debug(f"create_publication: {pub_img}")


    publication = Publication(**body.model_dump(exclude_unset=True))

    logger.debug(f"publication: {publication}")

    publication.user_id = user_id

    logger.debug(f"publication_user_id: {publication.user_id}")

    publication.image_id = pub_img.id

    logger.debug(f"create_publication: {publication}")

    db.add(publication)
    await db.commit()
    await db.refresh(publication)
    return publication
