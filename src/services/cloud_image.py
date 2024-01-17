import cloudinary.uploader
import qrcode
from PIL import Image

class ImageEditor:
    available_transformations = ["rotate", "apply_filter", "generate_qrcode"]
    @staticmethod
    def apply_transformation(file, transformation):
        if transformation == "rotate":
            return ImageEditor.rotate_image(file, 90)
        elif transformation == "apply_filter":
            return ImageEditor.apply_filter(file, 'grayscale')
        elif transformation == "generate_qrcode":
            return ImageEditor.generate_qrcode(file)
        else:
            raise ValueError("Invalid transformation type")

    @staticmethod
    def generate_qrcode(file):
        img = Image.open(file)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(img.tobytes())
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")

        img_qr_path = f'Temp/qrcode_{file.filename}'
        img_qr.save(img_qr_path)

        r = cloudinary.uploader.upload(img_qr_path, public_id=f'Temp/qrcode_{file.filename}', overwrite=True)
        current_qrcode_url = cloudinary.CloudinaryImage(f'Temp/qrcode_{file.filename}') \
            .build_url(width=250, height=250, crop='fill')

        return current_qrcode_url
