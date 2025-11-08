import requests

payload = {
   "event_id": "sod4b3c2c6f8iqr3onnhmifveo" #このidはtest-create-event.pyで作られたイベントのidを使用している（自分で変えるよう！！）
}

res = requests.post("http://localhost:8000/delete-event", json=payload)
print(res.json())