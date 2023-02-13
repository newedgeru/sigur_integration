import time
import requests

s = requests.Session()
headers = {"Connection": "keep-alive"}
counter = 0
while counter < 5:
    # response: requests.Response = requests.get(
    #     "http://192.168.1.127:8080/event", headers=headers
    # )
    response = s.get("http://192.168.1.127:8080/event")
    print(response.headers)
    print(response.text)
    time.sleep(1)
    counter += 1
