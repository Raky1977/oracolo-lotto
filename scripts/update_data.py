import requests

url = "https://lotto-api.onrender.com/lotto/latest"

try:
    r = requests.get(url, timeout=10)
    print("Status:", r.status_code)
    print("Risposta:", r.text)
except Exception as e:
    print("Errore:", e)
