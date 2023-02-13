import json
import time
from http import HTTPStatus

from flask import Flask, jsonify, request, Response

from iva_api import APIClient
from config import get_config


cfg = get_config()
print(cfg)

client = APIClient(
    storage_api=cfg.storage_api,
    search_api=cfg.search_api,
    dnn_api=cfg.dnn_api,
    data_storage_path=cfg.data_storage_path,
)


def get_id(suspect: dict) -> int:
    try:
        comment = suspect.get("comment", "{}") or "{}"
        print(comment)
        id_: int = int(json.loads(comment).get("id", 0))
    except Exception as e:
        print(e)
        return 0

    return id_


def init_skud2iva() -> dict:
    success, result = client.get_all_suspects_pages(1, 1_000_000)
    if not success:
        print(result)
        return Response(response=json.dumps({"error": result}), content_type="application/json")

    suspects = result.get("body", {}).get("suspects", {}) or {}

    data = {get_id(susp): susp.get("id") for _, susp in suspects.items()}

    return data


def create_app():
    app = Flask(__name__)

    # with app.app_context():
    #     g.skud2iva = init_skud2iva()

    return app

app = create_app()
# g.skud2iva = init_skud2iva()
class StorageInMemory():
    def __init__(self, data: dict):
        self.data: dict = data

    def get(self, key, default=None):
        return self.data.get(key, default)

    def pop(self, key):
        self.data.pop(key, default)

    def __setitem__(self, key, value):
        self.data[key] = value

skud2iva = StorageInMemory(init_skud2iva())

@app.get("/getchannels")
def get_channels():
    success, result = client.get_cameras()
    if not success:
        return jsonify({"error": result})

    channels = [{"id": k, "name": v.get("name")} for k, v in result.items()]

    return jsonify({"channels": channels})


# {'id': 26, 'name': 'qwer asdf zxcvtest', 'original_photo': '', 'group_id': 1, 'comment': '{"keys": ["2800BABABABA0000"], "photo_version": 1663062432, "id": 15}', 'active_till': 0, 'photo': '/suspects/suspect1674139822243211194.jpg'}
# from dataclasses import dataclass
# from typing import List


# @dataclass
# class Suspect:
#     id: int
#     name: str
#     original_photo: str
#     group_id: int
#     comment: str
#     active_till: int
#     photo: str

#     def __post_init__(self):
#         self.comment = json.loads(self.comment)


# @dataclass
# class SigurEmployee:
#     id: int
#     photoVersion: int
#     name: str
#     keys: List[str]

#     def __post_init__(self):
#         self.id = get_id(id)


@app.get("/getpersons")
def get_persons():
    success, result = client.get_all_suspects_pages(1, 1_000_000)
    if not success:
        return jsonify({"error": result})

    # suspects = [
    #     Suspect(**v)
    #     for _, v in (result.get("body", {}).get("suspects", {}) or {}).items()
    # ]
    suspects = result.get("body", {}).get("suspects", {}) or {}
    persons = [
        {
            "id": get_id(v),
            "photoVersion": json.loads(v.get("comment", {})).get("photo_version", 123),
            "name": v.get("name"),
            "keys": json.loads(v.get("comment", {})).get("keys", []),
        }
        for k, v in suspects.items()
    ]
    response = {"persons": persons}
    print(response)

    return jsonify(response)


import json
@app.post("/updateperson")
def update_person():
    data = json.loads(request.get_data())

    person_id = skud2iva.get(int(data.get("id")), None)
    if not person_id:
        success, result = client.create_person(data)
        if not success:
            if not result:
                print(result)
                return "", 200
            print(result)
            return "", 200

        iva_id = result.get("body")
        skud2iva[int(data.get("id"))] = iva_id
        print(f"[INFO]: Creating new employee with id {iva_id}")

        return "", 200

    success, result = client.update_person(data, str(person_id))
    if not success:
        if not result:
            print(result)
            return "", 200
        print(result)
        return "", 200

    print(f"[INFO]: Updating employee with id {person_id}")

    return "", 200


@app.get("/removeperson")
def remove_person():
    skud_id = int(request.args.get("id"))
    suspect_id = skud2iva.get(int(skud_id), 0)
    success, result = client.delete_suspect(suspect_id)
    if not success:
        print(result)
        return "", 400

    removed_id = skud2iva.pop(skud_id)
    print(f"[INFO]: Suspect with id {removed_id} was removed")
    return "", 200


@app.get("/event")
def event():
    data = {"type": "0ab0a061-12ec-4092-831d-33afe4f8a5f7"}
    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
