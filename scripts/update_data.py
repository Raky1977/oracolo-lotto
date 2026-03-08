import requests

url = "https://lotto-api.onrender.com/lotto/latest"

r = requests.get(url, timeout=10)
print(r.status_code)
print(r.text)
