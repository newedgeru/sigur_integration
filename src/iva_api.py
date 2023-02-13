import base64
import json
import time
from functools import wraps

import requests
from requests.auth import HTTPBasicAuth

from utils.imgs import convert_pillow

class Result:
    def __init__(self, status, body, message):
        self.status = status
        self.body = body
        self.message = message

    def is_failure(self):
        return self.status == 0

    def is_success(self):
        return self.status == 1

    def get_body(self):
        return self.body

    def get_message(self):
        return self.message


def with_error_handling(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            response: requests.Response = func(*args, **kwargs)
            response.raise_for_status()
        except Exception as e:
            return False, str(e)

        data = response.json()
        message = data.get("message")
        status = data.get("status")
        if status == 0:
            return False, message

        return True, data

    return wrapper


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        # first item in the args, ie `args[0]` is `self`
        # print(f"Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds")
        print(f"[PERF]: Function {func.__name__} Took {total_time:.4f} seconds")
        return result

    return timeit_wrapper


class APIClient:
    def __init__(
        self,
        scheme="http",
        apikey="ahjsdkas-lf10u7-ln7dju49",
        storage_api="storage_api:8080/api",
        dnn_api="dnnapi:8080/dnnapi",
        search_api="search:8089",
        notifier="notifier",
        data_storage_path="/storage/ivac",
    ):
        self.storage_api = f"{scheme}://{storage_api}"
        self.dnn_api = f"{scheme}://{dnn_api}"
        self.search_api = f"{scheme}://{search_api}"
        self.notifier = f"{scheme}://{notifier}"
        self.auth = HTTPBasicAuth("apikey", apikey)
        self.data_storage_path = data_storage_path

    @with_error_handling
    def get_face_from_image(self, image):
        response = requests.post(
            self.dnn_api + "/face-from-image",
            files={("image", image)},
            auth=self.auth,
            timeout=10,
        )
        return response

    @with_error_handling
    def add_suspect_by_face(self, suspect_data):
        response = requests.post(
            self.dnn_api + "/add-suspect-by-face",
            files=suspect_data,
            auth=self.auth,
            timeout=10,
        )
        return response

    @with_error_handling
    def get_embedding_from_face(self, face64):
        response = requests.post(
            self.dnn_api + "/embedding-from-face",
            files={("face64", (None, face64))},
            auth=self.auth,
            timeout=10,
        )
        return response

    @with_error_handling
    def get_all_suspects(self):
        response = requests.get(
            self.storage_api + "/suspects/get", auth=self.auth, timeout=10
        )
        return response

    @with_error_handling
    def get_suspect_by_id(self, suspect_id):
        response = requests.get(
            self.storage_api + f"/suspects/{suspect_id}", auth=self.auth, timeout=10
        )
        return response

    def getwithvector_all_suspects(self):
        response = requests.get(
            self.storage_api + "/suspects/getwithvector", auth=self.auth, timeout=10
        )
        return response

    @with_error_handling
    def get_all_suspects_pages(self, page, perPage):
        response = requests.get(
            self.storage_api + f"/suspects/get?page={page}&perPage={perPage}",
            auth=self.auth,
            timeout=10,
        )
        return response

    def search_detections(self, cam_id):
        response = requests.post(
            self.storage_api + f"/detections/search",
            files={("search_type", (None, "detections")), ("cam_id", (None, cam_id))},
            auth=self.auth,
            timeout=10,
        )
        return response

    def searchwithvector_detections(self, cam_id):
        response = requests.post(
            self.storage_api + f"/detections/searchwithvector",
            files={("search_type", (None, "detections")), ("cam_id", (None, cam_id))},
            auth=self.auth,
            timeout=10,
        )
        return response

    def search_detections_search_api(self, cam_id, vector, threshold=0.55):
        response = requests.post(
            self.search_api + f"/search_detection",
            files={
                ("search_type", (None, "detections")),
                ("cam_id", (None, cam_id)),
                ("vector", (None, vector)),
                ("threshold", (None, str(threshold))),
            },
            auth=self.auth,
            timeout=10,
        )
        return response

    def score_between(self, v1, v2):
        response = requests.post(
            self.search_api + "/score_between",
            json={"vector_one": v1, "vector_two": v2},
            auth=self.auth,
            timeout=10,
        )

        return response

    @with_error_handling
    def delete_suspect(self, suspect_id):
        response = requests.post(
            self.search_api + "/remove",
            files={("id", (None, str(suspect_id)))},
            auth=self.auth,
            timeout=10,
        )

        return response

    @with_error_handling
    def update_suspect(self, data):
        response = requests.post(
            self.search_api + "/update_suspect", files=data, auth=self.auth, timeout=10
        )

        return response

    def search_suspect(self, vector):
        response = requests.post(
            self.search_api + "/search",
            files={("vector", (None, vector))},
            auth=self.auth,
            timeout=10,
        )

        return response

    @with_error_handling
    def search_suspects(self, vector):
        response = requests.post(
            self.search_api + "/search_suspects",
            files={("vector", (None, vector))},
            auth=self.auth,
            timeout=10,
        )

        return response

    def upload_video(self, video, filename="video"):
        response = requests.post(
            self.storage_api + "/videos/upload",
            files={("video", (filename, video))},
            auth=self.auth,
            timeout=10,
        )
        return response

    def create_new_video(self, data):
        response = requests.post(
            self.storage_api + "/videos/new", files=data, auth=self.auth, timeout=10
        )
        return response

    def update_video(self, data):
        response = requests.post(
            self.storage_api + "/videos/update", files=data, auth=self.auth, timeout=10
        )
        return response

    def delete_video(self, id):
        response = requests.post(
            self.storage_api + "/videos/delete",
            files={("id", (None, id))},
            auth=self.auth,
            timeout=10,
        )
        return response

    def get_videos(self):
        response = requests.get(
            self.storage_api + "/videos/all", auth=self.auth, timeout=10
        )
        return response

    @with_error_handling
    def create_detections(self, json):
        response = requests.post(
            self.notifier + "/inputs/track",
            data=json,
            headers={"Content-Type": "application/json"},
            auth=self.auth,
            timeout=10,
        )
        return response

    @with_error_handling
    def get_cameras(self):
        response = requests.post(
            self.storage_api + "/cameras/all",
            auth=self.auth,
            timeout=10,
        )
        return response

    def _make_api_url(self, scheme, host, port, api_name=None):
        if not api_name:
            return f"{scheme}://{host}:{port}"

        return f"{scheme}://{host}:{port}/{api_name}"

    def create_person(self, data):
        person_id = int(data.get("id"))
        photo = data.get("photo")
        name = data.get("name")
        keys = data.get("keys")
        photo_version = data.get("photoVersion")

        if not photo:
            return False, f"no photo for {person_id}"

        photo_bytes = base64.b64decode(photo)
        photo_bytes = convert_pillow(photo_bytes)

        success, result = self.get_face_from_image(photo_bytes)
        if not success:
            return False, result

        face64 = next(iter(result.get("body", {}).get("faces", [])), None)

        employee_data = {
            ("face64", (None, face64)),
            ("original_img64", (None, "")),
            ("name", (None, name)),
            ("search_detection_bool", (None, "false")),
            ("override_suspect", (None, "false")),
            ("threshold", (None, "")),
            ("group_id", (None, "")),
            ("active_till", (None, "")),
            (
                "comment",
                (
                    None,
                    json.dumps(
                        {"keys": keys, "photo_version": photo_version, "id": person_id}
                    ),
                ),
            ),
        }

        success, result = self.add_suspect_by_face(employee_data)
        if not success:
            return False, result

        return True, result

    def update_person(self, data: dict, iva_id: int):
        keys = data.get("keys", [])
        photo_version = data.get("photoVersion")
        person_id = int(data.get("id"))
        photo = data.get("photo")

        if not photo:
            return False, f"no photo for {person_id}"

        photo_bytes = base64.b64decode(photo)
        photo_bytes = convert_pillow(photo_bytes)

        success, result = self.get_face_from_image(photo_bytes)
        if not success:
            print(result)
            return False, result

        face64 = next(iter(result.get("body", {}).get("faces", [])), None)

        t_now = int(time.time() * 1_000_000_000)
        file_name = f"suspect{t_now}"
        file_path = f"{self.data_storage_path}/suspects/{file_name}.jpg"

        face64_bytes = base64.b64decode(face64)
        with open(file_path, "wb") as image:
            image.write(face64_bytes)

        success, result = self.get_embedding_from_face(face64)
        if not success:
            print(result)
            return False, result

        embedding = next(iter(result.get("body").get("vector")), None)

        update_data = {
            ("id", (None, iva_id)),
            ("vector", (None, embedding)),
            ("name", (None, data.get("name"))),
            ("file_path", (None, f"/suspects/{file_name}.jpg")),
            (
                "comment",
                (
                    None,
                    json.dumps(
                        {"keys": keys, "photo_version": photo_version, "id": person_id}
                    ),
                ),
            ),
        }

        success, result = self.update_suspect(update_data)
        if not success:
            print(result)
            return False, result

        return True, result
