import io

import qrcode


# Создайте объект QRCode


async def generate_qr_code_byte(cloudinary_link):
    """
    Generate QR code byte.
    :param cloudinary_link: cloudinary link: cloudinary link from request body
    :return: qr code byte in bytes

    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # Добавьте данные в объект QRCode
    qr.add_data(cloudinary_link)

    # Создайте изображение QR-кода
    img = qr.make_image(fill_color="black", back_color="white")
    # Преобразуйте изображение QR-кода в байты
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr)
    img_byte_arr = img_byte_arr.getvalue()

    return img_byte_arr  # Возвращаем изображение QR-кода в байтах
