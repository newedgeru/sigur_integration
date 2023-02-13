import cv2
import numpy as np

with open("tests/sigur_failed_1.jpeg", "rb") as f:
    photo_bytes = f.read()

# CV2
nparr = np.frombuffer(photo_bytes, np.uint8)
img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

cv2.imwrite('tests/resized_img.jpeg', img_np)

print(img_np.tobytes())
