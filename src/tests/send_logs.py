import requests
import json
import time

with open("logs/app.logs") as logs:
    log_lines = logs.readlines()

# print(log_lines[0])
for line in log_lines:
    responce = requests.post("http://localhost:8080/updateperson", json=json.loads(line))
    print(responce.status_code)
    # time.sleep(0.5)