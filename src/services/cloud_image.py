import cloudinary
from cloudinary.uploader import upload
from cloudinary.api import update, delete_resources_by_prefix
from src.conf.config import config


class CloudinaryService:
    def __init__(self):
        self.configure_cloudinary()

        self.command_transformation = {
            "left": self.move_left,
            "right": self.move_right,
            "filter": self.append_filter
        }

    def configure_cloudinary(self):
        """
        Configure cloudinary. See https://cloudinary.com/documentation/python
        :return: None

        """
        cloudinary.config(
            cloud_name=config.CLOUDINARY_NAME,
            api_key=config.CLOUDINARY_API_KEY,
            api_secret=config.CLOUDINARY_API_SECRET,
        )

    def save_to_temp(self, file, email: str) -> str:
        """
        Save file to temp folder
        :param file: file object: image file or video file etc.
        :param email: user email: user email from request body
        :return: public_id: cloudinary public id of image file

        """
        result = upload(file, folder=f"{email}/temp/", use_filename=True, unique_filename=True)
        public_id = result['public_id']
        return public_id

    def replace_temp_to_id(self, email: str, public_id: str):
        """
        Replace temp folder to id folder in cloudinary account
        :param email: user email: user email from request body
        :param public_id: cloudinary public id of image file
        :return: current folder path in cloudinary account

        """
        current_folder_path = f"{email}/current/{public_id}/"
        update_result = update(
            public_id=f"{email}/temp/{public_id}",
            folder=current_folder_path
        )
        return current_folder_path

    def del_temp(self, email, public_id) -> None:
        """
        Delete temp folder in cloudinary account

        :param email: user email: user email from request body
        :param public_id: cloudinary public id of image file
        :return: None

        """
        delete_resources_by_prefix(f"{email}/temp/{public_id}")

    def move_left(self, email, public_id):
        self.apply_transformation(public_id, {'angle': 90})

    def move_right(self, email, public_id):
        self.apply_transformation(public_id, {'angle': -90})

    def append_filter(self, email, public_id, filter_name):
        self.apply_transformation(public_id, {'effect': filter_name})

    def apply_transformation(self, public_id, transformation):
        update(
            public_id=public_id,
            transformation=transformation
        )


cloudinary_service = CloudinaryService()

email = "user@example.com"
file_path = "C:\\Users\\chorn\\OneDrive\\Desktop\\info.jpg"
public_id = cloudinary_service.save_to_temp(file_path, email)

current_folder_path = cloudinary_service.replace_temp_to_id(email, public_id)

cloudinary_service.move_left(email, public_id)
cloudinary_service.move_right(email, public_id)
cloudinary_service.append_filter(email, public_id, 'grayscale:50:0')

# cloudinary_service.del_temp(email, public_id)
