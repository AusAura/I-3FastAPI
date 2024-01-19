from enum import Enum
from typing import BinaryIO, Any, Dict

import cloudinary
from cloudinary import uploader
from cloudinary.api import delete_resources_by_prefix, update
from cloudinary.api_client.execute_request import Response
from cloudinary.uploader import upload, destroy, rename
from cloudinary.exceptions import Error as CloudinaryError
from cloudinary.utils import cloudinary_url

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
            "round_face": self.round_face,
        }

    per_folder = PermissionsFolder

    def __call__(self):
        return self

    def get_cloud_id(self, email: str, postfix: str, post_id: int | None = None,
                     folder: str | None = None) -> str | None:

        if folder is None: folder = self.per_folder.temp.name

        if folder not in self.per_folder.array():
            raise CloudinaryServiceError(f"Folder '{folder}' not allowed")

        public_id = f"{email}/{folder}/{postfix}" if post_id is None else f"{email}/{folder}/{post_id}/{postfix}"

        try:
            cloudinary.api.resource(public_id)
            return public_id
        except CloudinaryError as err:
            if msg.CLOUD_RESOURCE_NOT_FOUND in str(err):
                return None
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

        if self.get_cloud_id(email, postfix):
            result = rename(from_public_id=from_public_id, to_public_id=to_public_id)
        else:
            return {postfix: None}

        return {postfix: result['secure_url']}

    @staticmethod
    def round_face() -> dict[str, int | str]:
        transformation = {
            "gravity": "face",
            "height": 200,
            "width": 200,
            "crop": "thumb",
            "radius": "max",
        }
        return transformation

    def apply_transformation(self, key: str, cloud_current_id, cloud_update_id) -> str:

        if key not in self.command_transformation:
            raise CloudinaryServiceError(f"Invalid transformation key: {key}")

        cloud_id = cloud_update_id if cloud_update_id is not None else cloud_current_id
        if cloud_id is None:
            raise CloudinaryServiceError(msg.PLEASE_UPLOAD_IMAGE)

        res_url = cloudinary.CloudinaryImage(cloud_id).build_url(**self.command_transformation.get(key)())
        upload(res_url, public_id=cloud_update_id, overwrite=True)
        return res_url


cloud_img_service = CloudinaryService()

TRANSFORMATION_KEYS = cloud_img_service.command_transformation.keys()
