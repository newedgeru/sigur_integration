import cv2
import numpy as np
import tempfile
import time


def resize(photo_bytes: bytes) -> bytes:
    # print(photo_bytes)
    # CV2
    image = np.frombuffer(photo_bytes, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    success, encoded_image = cv2.imencode('.jpeg', image)
    content2 = encoded_image.tobytes()

    # return_value = b''
    # with tempfile.NamedTemporaryFile("r", delete=False) as tmp:
    #     cv2.imwrite(f"{tmp.name}.jpeg", img_np)
    #     time.sleep(0.1)
    #     with open(f"{tmp.name}.jpeg", "rb") as f:
    #         return_value = f.readall()

    # resized_img = cv2.resize(img_np, None, fx=1, fy=1, interpolation=cv2.INTER_CUBIC)

    # success, img = cv2.imencode('.jpeg', resized_img)
    # a = img.tostring()

    return content2
