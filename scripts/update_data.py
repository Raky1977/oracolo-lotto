import json
import requests
from datetime import datetime

url = "https://lotto-api.onrender.com/lotto/latest"

def update():

    r = requests.get(url, timeout=10)
    data = r.json()

    risultato = {
        "lotto": [{
            "data": datetime.now().strftime("%d/%m/%Y"),
            "ruote": {
                "Bari": data.get("bari", []),
                "Cagliari": data.get("cagliari", []),
                "Firenze": data.get("firenze", []),
                "Genova": data.get("genova", []),
                "Milano": data.get("milano", []),
                "Napoli": data.get("napoli", []),
                "Palermo": data.get("palermo", []),
                "Roma": data.get("roma", []),
                "Torino": data.get("torino", []),
                "Venezia": data.get("venezia", []),
                "Nazionale": data.get("nazionale", [])
            }
        }],
        "superenalotto": [],
        "last_global_update": datetime.now().strftime("%d/%m/%Y %H:%M")
    }

    with open("estrazioni.json","w",encoding="utf-8") as f:
        json.dump(risultato,f,indent=2,ensure_ascii=False)

    print("JSON aggiornato")

update()
