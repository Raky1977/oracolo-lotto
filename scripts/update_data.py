import json
import requests
from datetime import datetime

def get_api_data():
    # Usiamo l'API stabile per i dati reali
    url = "https://lotto-api.onrender.com/lotto/latest"
    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            api_data = response.json()
            
            # Mappatura dei nomi per l'app (iniziale maiuscola)
            ruote_mappa = {
                "bari": "Bari", "cagliari": "Cagliari", "firenze": "Firenze",
                "genova": "Genova", "milano": "Milano", "napoli": "Napoli",
                "palermo": "Palermo", "roma": "Roma", "torino": "Torino",
                "venezia": "Venezia", "nazionale": "Nazionale"
            }
            
            lotto_entry = {
                "data": api_data.get("date", datetime.now().strftime("%d/%m/%Y")),
                "ruote": {}
            }
            
            # Trasformiamo i dati dell'API nel formato che serve alla tua App
            for key, beauty_name in ruote_mappa.items():
                if key in api_data:
                    lotto_entry["ruote"][beauty_name] = api_data[key]
            
            return lotto_entry
    except Exception as e:
        print(f"Errore API: {e}")
    return None

def update():
    nuovi_dati_lotto = get_api_data()
    
    if nuovi_dati_lotto and nuovi_dati_lotto["ruote"]:
        # Carichiamo il file esistente per non perdere il Superenalotto o lo storico
        try:
            with open('estrazioni.json', 'r', encoding='utf-8') as f:
                database = json.load(f)
        except:
            database = {"lotto": [], "superenalotto": []}

        # Evitiamo duplicati: aggiungi solo se la data è nuova
        ultima_data = database["lotto"][0]["data"] if database["lotto"] else ""
        
        if nuovi_dati_lotto["data"] != ultima_data:
            database["lotto"].insert(0, nuovi_dati_lotto)
            # Teniamo le ultime 20 estrazioni
            database["lotto"] = database["lotto"][:20]
            print(f"Dati REALI inseriti per il {nuovi_dati_lotto['data']}")
        else:
            print("Dati già aggiornati all'ultima estrazione.")

        database["last_global_update"] = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Scrittura finale sul file
        with open('estrazioni.json', 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=4, ensure_ascii=False)
    else:
        print("Impossibile recuperare dati validi dall'API.")

if __name__ == "__main__":
    update()
