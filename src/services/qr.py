from typing import Iterable

import qrcode
from qrcode.image.pure import PyPNGImage

QR_PICTURES_DIR = '../../qr_pictures/'


# def get_images(data: Iterable[str]) -> list[PyPNGImage]:
#     return [type(qrcode.make(item)) for item in data]
qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
)


def get_image(data: str) -> PyPNGImage:
    qr.clear()
    qr.add_data(data)
    return qr.make_image(fill_color='green', back_color='white')


def get_images(data: Iterable[str]) -> list[PyPNGImage]:
    return [get_image(item) for item in data]
