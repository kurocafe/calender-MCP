import requests

res = requests.get("http://localhost:8000/list-events")
print(res.json())