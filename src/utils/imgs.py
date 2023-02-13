from PIL import Image
import io


def convert_pillow(photo_bytes: bytes) -> bytes:
    image = Image.open(io.BytesIO(photo_bytes))
    img_bytes = io.BytesIO()
    image.save(img_bytes, format = "JPEG")
    return img_bytes.getvalue()
