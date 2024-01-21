from typing import Any, Type

from cloudinary.exceptions import Error as CloudinaryError

from src.utils.my_logger import logger


class CloudinaryServiceError(Exception):
    def __init__(self, message: str, *args: Any) -> None:
        super().__init__(message, *args)


class CloudinaryResourceNotFoundError(CloudinaryServiceError):
    pass


class CloudinaryLoadingError(CloudinaryServiceError):
    pass


cloud_errors = {
    "Resource not found": CloudinaryResourceNotFoundError,
    "Error in loading": CloudinaryLoadingError
}


def manager_cloudinary_error(error_message: str) -> CloudinaryServiceError | CloudinaryError:

    for err_msg, cloud_error in cloud_errors.items():
        if err_msg in error_message:
            return cloud_error(error_message)
    logger.error(f"New error massage: add to cloud_errors by msg:{error_message}")
    return CloudinaryError(error_message)
