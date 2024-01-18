from enum import Enum
from typing import BinaryIO, Any

import cloudinary
from cloudinary.api import delete_resources_by_prefix, update
from cloudinary.uploader import upload, destroy, rename
from cloudinary.exceptions import Error as CloudinaryError

from src.conf.config import config
from src.utils.my_logger import logger
import src.messages as msg


class CloudinaryServiceError(Exception):
    """Основной класс для ошибок CloudinaryService."""

    def __init__(self, message: str, *args: Any) -> None:
        super().__init__(*args)
        self.message = message


class PermissionsFolder(Enum):
    temp = "temp"
    publications = "publications"
    avatar = "avatar"

    @classmethod
    def array(cls) -> list[str]:
        return [field.name for field in cls]


class CloudinaryService:
    def __init__(self):
        cloudinary.config(
            cloud_name=config.CLOUDINARY_NAME,
            api_key=config.CLOUDINARY_API_KEY,
            api_secret=config.CLOUDINARY_API_SECRET,
        )

        self.command_transformation = {
            "left": self.move_left,
            "right": self.move_right,
            "filter": self.append_filter
        }

    per_folder = PermissionsFolder

    def __call__(self):
        return self

    def image_exists(self, email: str, postfix: str, post_id: int | None = None, folder: str | None = None) -> bool:

        if folder is None: folder = self.per_folder.temp.name
        public_id = f"{email}/{folder}/{post_id}/{postfix}"

        try:
            cloudinary.api.resource(public_id)
            return True
        except CloudinaryError as err:
            if msg.CLOUD_RESOURCE_NOT_FOUND in str(err):
                return False
            raise CloudinaryServiceError(str(err))

    def save_by_email(self, file: BinaryIO, email: str, postfix: str, post_id: int | None = None,
                      folder: str | None = None) -> str:

        if folder is None: folder = self.per_folder.temp.name

        if folder not in self.per_folder.array():
            raise CloudinaryServiceError(f"Folder '{folder}' not allowed")

        public_id = f"{email}/{folder}/{postfix}" if post_id is None else f"{email}/{folder}/{post_id}/{postfix}"

        result = upload(file, public_id=public_id, overwrite=True)

        logger.info(f'upload image({folder}) from user: {email} id: {result["public_id"]}')
        return result['secure_url']

    def replace_temp_to_publications(self, email: str, postfix: str, post_id: int) -> dict[str, str]:

        from_public_id = f"{email}/{self.per_folder.temp.name}/{postfix}"
        to_public_id = f"{email}/{self.per_folder.publications.name}/{post_id}/{postfix}"

        if self.image_exists(email, postfix, post_id):
            result = rename(from_public_id=from_public_id, to_public_id=to_public_id)
        else:
            return {postfix: None}

        return {postfix: result['secure_url']}

    @staticmethod
    def move_left(email, public_id):
        CloudinaryService.apply_transformation(public_id, {'angle': 90})

    @staticmethod
    def move_right(email, public_id):
        CloudinaryService.apply_transformation(public_id, {'angle': -90})

    @staticmethod
    def append_filter(email, public_id, filter_name):
        CloudinaryService.apply_transformation(public_id, {'effect': filter_name})

    @staticmethod
    def apply_transformation(public_id, transformation):
        update(
            public_id=public_id,
            transformation=transformation
        )


cloud_img_service = CloudinaryService()

TRANSFORMATION_KEYS = cloud_img_service.command_transformation.keys()
