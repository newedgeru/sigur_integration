import requests
import json
import time
import base64
import requests
import cv2
import numpy as np
from PIL import Image

# from imgs import resize
from requests.auth import HTTPBasicAuth
import io

def resize(photo_bytes: bytes) -> bytes:
    image = np.frombuffer(photo_bytes, np.uint8)

    success, encoded_image = cv2.imencode('.jpg', image)
    if not success:
        print('faield to save as .jpeg')
    img_np = cv2.imdecode(image, cv2.IMREAD_COLOR)
    success, encoded_image = cv2.imencode('.jpg', img_np)

    return encoded_image.tobytes()

def resize_pil(photo_bytes: bytes) -> bytes:
    image = Image.open(io.BytesIO(photo_bytes))
    img_bytes = io.BytesIO()
    image.save(img_bytes, format = "JPEG")
    return img_bytes.getvalue()


apikey="ahjsdkas-lf10u7-ln7dju49"

with open("logs/app.logs") as logs:
    log_lines = logs.readlines()


DNN_API="localhost:19090/dnnapi/dnnapi"
# print(log_lines[0])
for line in log_lines:
    photo = base64.b64decode(json.loads(line).get("photo"))
    if not photo:
        continue
    image = resize(photo)

    response = requests.post("http://localhost:19090/dnnapi/dnnapi/face-from-image", files={("image", image)}, auth=HTTPBasicAuth('apikey', apikey))
    print(response.status_code)
    print(response.text)


    # def get_face_from_image(self, image):
    #     response = requests.post(
    #         self.dnn_api + "/face-from-image",
    #         files={("image", image)},
    #         auth=self.auth,
    #         timeout=10,
    #     )
    #     return response