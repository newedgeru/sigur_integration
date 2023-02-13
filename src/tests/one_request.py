import requests
import json
import time

with open("logs/app.logs") as logs:
    log_lines = logs.readlines()

data = log_lines[0]
print(type(data))
data = '{"id": 3426, "name": "Омельяненко Игорь Игоревич", "photoVersion": 0, "photo": "", "keys": ["1862296000000000"]}'
# data = {"id": 3426, "name": "Омельяненко Игорь Игоревич", "photoVersion": 0, "photo": "", "keys": ["1862296000000000"]}
responce = requests.post("http://localhost:8080/updateperson", json=json.loads(data))
print(responce.status_code)