import requests

payload = {
    "summary": "Lunch",
    "description": "Sushi",
    "location": "Tokyo",
    "start": "2025-02-15T12:00:00+09:00",
    "end": "2025-02-15T13:00:00+09:00"
}

res = requests.post("http://localhost:8000/create-event", json=payload)
print(res.json())