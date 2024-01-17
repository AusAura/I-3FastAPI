import cloudinary
from cloudinary.api import delete_resources_by_prefix, update
from cloudinary.uploader import upload

from src.conf.config import config


class CloudinaryService:
    def __init__(self):
        self.configure_cloudinary()

    def configure_cloudinary(self):
        cloudinary.config(
            cloud_name=config.CLOUDINARY_NAME,
            api_key=config.CLOUDINARY_API_KEY,
            api_secret=config.CLOUDINARY_API_SECRET,
        )

    @staticmethod
    def save_to_temp(file, email: str) -> str:
        result = upload(file, folder=f"{email}/temp/", use_filename=True, unique_filename=True)
        public_id = result['public_id']
        return public_id

    @staticmethod
    def replace_temp_to_id(email: str, public_id: str):
        try:
            current_folder_path = f"{email}/current/{public_id}/"
            update_result = update(
                public_id=f"{email}/temp/{public_id}",
                folder=current_folder_path
            )
            return current_folder_path
        except cloudinary.exceptions.NotFound as e:
            return None

    @staticmethod
    def del_temp(email, public_id) -> None:
        delete_resources_by_prefix(f"{email}/temp/{public_id}")

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
