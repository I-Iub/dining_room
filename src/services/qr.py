import io
from typing import Iterable

import cv2
import qrcode
import numpy as np
from qrcode.image.pure import PyPNGImage


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


def decode(buffer: io.BytesIO) -> str:
    detect = cv2.QRCodeDetector()
    array = np.frombuffer(buffer.read(), dtype=np.uint8)
    obj = cv2.imdecode(array, 0)
    data, *_ = detect.detectAndDecode(obj)
    return data
