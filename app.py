import json
import time

from flask import Flask, jsonify, request

from iva_api import APIClient

app = Flask(__name__)

client = APIClient(
    storage_api="localhost:19090/storage/api",
    search_api="localhost:19090/search_api",
    dnn_api="localhost:19090/dnnapi/dnnapi",
    data_storage_path="/home/konstantin/IVACV/data_storage",
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


def init_skud2iva():
    success, result = client.get_all_suspects_pages(1, 1_000_000)
    if not success:
        return jsonify({"error": result})

    suspects = result.get("body", {}).get("suspects", {}) or {}

    data = {get_id(susp): susp.get("id") for _, susp in suspects.items()}

    return data


skud2iva = init_skud2iva()


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


@app.post("/updateperson")
def update_person():
    data = request.json

    person_id = skud2iva.get(int(data.get("id")), None)
    if not person_id:
        success, result = client.create_person(data)
        if not success:
            print(result)
            return "", 400

        iva_id = result.get("body")
        skud2iva[int(data.get("id"))] = iva_id
        print(f"[INFO]: Creating new employee with id {iva_id}")

        return "", 200

    success, result = client.update_person(data, str(person_id))
    if not success:
        return "", 400

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
