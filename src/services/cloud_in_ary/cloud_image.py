from enum import Enum
from typing import BinaryIO

import cloudinary
from cloudinary.api import delete_resources_by_prefix
from cloudinary.uploader import upload, rename
from cloudinary.exceptions import Error as CloudinaryError

from src.conf.config import config
from src.services.cloud_in_ary.errors import CloudinaryServiceError, CloudinaryResourceNotFoundError
from src.services.cloud_in_ary.transformations import TRANSFORMATIONS
from src.utils.my_logger import logger
import src.messages as msg


class PermissionsFolder(Enum):
    """
    Permissions folder in cloudinary {email}/{folder}/
    """
    temp = "temp"
    publications = "publications"
    avatar = "avatar"

    @classmethod
    def array(cls) -> list[str]:
        """
        Get list of permissions folder
        :return: list of permissions folder
        """
        return [field.name for field in cls]


class CloudinaryService:
    def __init__(self):
        """
        Init cloudinary config
        """
        cloudinary.config(
            cloud_name=config.CLOUDINARY_NAME,
            api_key=config.CLOUDINARY_API_KEY,
            api_secret=config.CLOUDINARY_API_SECRET,
        )

        self.command_transformation: dict = TRANSFORMATIONS  # src.services.transformations

    per_folder = PermissionsFolder  # permissions folder in cloudinary {email}/{folder}/

    def __call__(self):
        """
        special method for calling object in dependency
        :return: object of CloudinaryService
        """
        return self

    def get_cloud_id(self, email: str, postfix: str, post_id: int | None = None,
                     folder: str | None = None) -> str | None:
        """
        Get public_id(cloud_id) relative path in cloudinary
        also usage to check if resource exists
        :param email: user email main folder in cloudinary
        :param postfix: name of image in cloudinary
        :param post_id: default None, publication id also folder in cloudinary
        :param folder: default None ("temp"), name of folder in cloudinary
        :return: cloud_id if resource exists else None. for example: "mail@example.com/temp/current_img.png"
        :raise CloudinaryResourceNotFoundError: if resource not found
        :raise CloudinaryServiceError: if folder not allowed in permissions
        """
        # if None -  set default folder "temp"
        if folder is None: folder = self.per_folder.temp.name

        if folder not in self.per_folder.array():
            raise CloudinaryServiceError(f"Folder '{folder}' not allowed")

        # build cloud_id
        cloud_id = f"{email}/{folder}/{postfix}" if post_id is None else f"{email}/{folder}/{post_id}/{postfix}"

        try:
            # check if resource exists
            cloudinary.api.resource(cloud_id)
            return cloud_id
        except CloudinaryError as err:
            if msg.CLOUD_RESOURCE_NOT_FOUND in str(err):
                return None
            raise CloudinaryServiceError(str(err))

    def save_by_email(self, data: BinaryIO | str, email: str, postfix: str, post_id: int | None = None,
                      folder: str | None = None) -> str:
        """
        Upload image to cloudinary

        Build cloud_id relative path (cloud_id) by parameters, for example:
        /{email}/{folder}/{postfix} or /{email}/{folder}/{post_id}/{postfix}
        and upload image to cloudinary, overwrite if resource with same cloud_id already exists

        :param data: binary data (image)
        :param email: user email main folder in cloudinary
        :param postfix: name of image in cloudinary
        :param post_id: default None, publication id also folder in cloudinary
        :param folder: default None ("temp"), name of folder in cloudinary
        :return: cloudinary url of uploaded image with path by parameters
        :raise CloudinaryServiceError: if folder not allowed in permissions
        """
        if folder is None: folder = self.per_folder.temp.name

        if folder not in self.per_folder.array():
            raise CloudinaryServiceError(f"Folder '{folder}' not allowed")

        # build cloud_id
        cloud_id = f"{email}/{folder}/{postfix}" if post_id is None else f"{email}/{folder}/{post_id}/{postfix}"

        # upload image
        result = upload(data, public_id=cloud_id, overwrite=True)

        logger.info(f'upload image({folder}) from user: {email} id: {result["public_id"]}')
        return result['secure_url']

    def replace_temp_to_publications(self, email: str, postfix: str, post_id: int) -> dict[str, str]:
        """
        Replace image from {email}/temp to {email}/publications{publication_id}
        :param email: user email main folder in cloudinary
        :param postfix: name of image in cloudinary
        :param post_id: default None, publication id also folder in cloudinary
        :return: dict {postfix: cloudinary url | None}
        """
        # build old and new cloud_id
        from_public_id = f"{email}/{self.per_folder.temp.name}/{postfix}"
        to_public_id = f"{email}/{self.per_folder.publications.name}/{post_id}/{postfix}"

        # check if resource exists by cloud_id {email}/temp/{postfix}
        if self.get_cloud_id(email, postfix):
            # replace {email}/temp/{postfix} to {email}/publications{publication_id}{postfix}
            result = rename(from_public_id=from_public_id, to_public_id=to_public_id)
        else:
            return {postfix: None}

        return {postfix: result['secure_url']}

    def delete_by_email(self, email: str, post_id: int, folder: str, postfixes: list[str]) -> None:
        """
        Delete image from cloudinary
        build cloud_id relative path (cloud_id) by parameters
        for example: /{email}/{folder}/{postfix} or /{email}/{folder}/{post_id}/{postfix}
        :param email: user email main folder in cloudinary
        :param post_id: default None, publication id also folder in cloudinary
        :param folder: name of folder in cloudinary
        :param postfixes: name of image in cloudinary to delete
        :return: None
        :raise CloudinaryServiceError: if folder not allowed in permissions
        """
        if folder not in self.per_folder.array():
            raise CloudinaryServiceError(f"Folder '{folder}' not allowed")

        # build cloud_id without postfix
        folder_path = f"{email}/{folder}/{post_id}"

        # delete images in folder with named postfix
        for postfix in postfixes:
            try:
                delete_resources_by_prefix(prefix=f"{folder_path}/{postfix}")
            except CloudinaryError as err:
                if msg.CLOUD_RESOURCE_NOT_FOUND in str(err):
                    continue
                raise CloudinaryServiceError(str(err))

        # delete folder if empty
        cloudinary.api.delete_folder(folder_path)

    def apply_transformation(self, key: str, email: str, current_postfix: str, updated_postfix: str,
                             post_id: int | None = None, folder: str | None = None) -> str:
        """
        Apply transformation to image by key

        Build cloud_id relative path by parameters
        for example: /{email}/{folder}/{postfix} or /{email}/{folder}/{post_id}/{postfix}
        if updated_postfix is None then use current_postfix and save to updated_postfix

        :param key: transformation key
        :param email: user email main folder in cloudinary
        :param current_postfix: name of image in cloudinary
        :param updated_postfix: name of image in cloudinary
        :param post_id: publication id also folder in cloudinary
        :param folder: default None ("temp"), name of folder in cloudinary
        :return: url of transformed image
        :raise CloudinaryServiceError: if folder not allowed in permissions
        :raise CloudinaryResourceNotFoundError: if resource not found
        :raise CloudinaryServiceError: if transformation key not allowed
        """
        if key not in self.command_transformation:
            raise CloudinaryServiceError(f"Invalid transformation key: {key}")

        # exists check and build cloud_id if .../updated_postfix is None then use .../current_postfix else rise error
        if (cloud_id := self.get_cloud_id(email=email, post_id=post_id, folder=folder, postfix=updated_postfix)) is None:
            if (cloud_id := self.get_cloud_id(email=email, post_id=post_id, folder=folder, postfix=current_postfix)) is None:
                raise CloudinaryResourceNotFoundError(msg.CLOUD_RESOURCE_NOT_FOUND)

        # Build the URL with the specified transformation
        transformed_url = cloudinary.CloudinaryImage(cloud_id).build_url(**self.command_transformation.get(key))

        # Create a new public ID for the transformed image
        logger.info(f'upload image(transformed) from user: {cloud_id}')
        # Upload the transformed image as a new asset with the new public ID
        transformed_url = self.save_by_email(transformed_url, email, updated_postfix, post_id, folder)

        return transformed_url


cloud_img_service = CloudinaryService()

TRANSFORMATION_KEYS = cloud_img_service.command_transformation.keys()
