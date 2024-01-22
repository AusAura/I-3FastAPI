from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from starlette import status
from src.schemas.publications import TempImage
from src.services.auth import auth_service
from src.services.image_editor import ImageEditor
from src.utils.my_logger import logger
from src.database.models import User

router = APIRouter(prefix='/image', tags=['Image Transformations'])

@router.post('/transform', status_code=status.HTTP_201_CREATED, response_model=TempImage)
async def transform_image(file: UploadFile = File(),
                           transformation: str = Query(..., description="Type of transformation to apply"),
                           user: User = Depends(auth_service.get_current_user)):
    if transformation not in ImageEditor.available_transformations:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid transformation type")

    current_image_url = ImageEditor.apply_transformation(file.file, transformation)
    logger.info(f'transformed image from user: {user.email} url: {current_image_url}')
    return TempImage(**{"current_img": current_image_url})

@router.post('/generate_qrcode', status_code=status.HTTP_201_CREATED, response_model=TempImage)
async def generate_qrcode(file: UploadFile = File()):
    # Generate QR code
    img = Image.open(file.file)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(img.tobytes())
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")

    # Save QR code image
    img_qr_path = f'Temp/qrcode_{file.filename}'
    img_qr.save(img_qr_path)

    # Upload QR code image to Cloudinary
    r = cloudinary.uploader.upload(img_qr_path, public_id=f'Temp/qrcode_{file.filename}', overwrite=True)

    current_qrcode_url = cloudinary.CloudinaryImage(f'Temp/qrcode_{file.filename}').build_url(width=250, height=250, crop='fill')

    logger.info(f'generated QR code url: {current_qrcode_url}')

    return TempImage(**{"current_img": current_qrcode_url})