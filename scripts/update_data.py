import requests
import json

print("Script partito")

url = "https://lotto-api.onrender.com/lotto/latest"

try:
    r = requests.get(url, timeout=10)
    r.raise_for_status()  # genera eccezione se status != 200
    data = r.json()       # prende direttamente il JSON dall'API

    print("Dati ricevuti:", data)

    # Scrivi nel file
    with open('estrazioni.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("SUCCESSO: JSON aggiornato")

except requests.exceptions.RequestException as e:
    print("Errore nella richiesta:", e)
