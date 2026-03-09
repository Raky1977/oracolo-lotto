import json
import requests
from datetime import datetime
import os

def get_data_open_source():
    # Puntiamo a una collezione di dati Lotto che viene aggiornata regolarmente
    # e che risiede su infrastrutture cloud (GitHub/S3) che non bloccano GitHub Actions.
    urls = [
        "https://raw.githubusercontent.com/fede-94/lotto-italia/main/lotto.json",
        "https://api.allorigins.win/get?url=https://www.estrazionedellotto.it/res/lotto.json"
    ]
    
    for url in urls:
        try:
            print(f"Tentativo di connessione a: {url}")
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                # Gestione se il dato è dentro il wrapper AllOrigins
                if "allorigins" in url:
                    data = json.loads(response.json()['contents'])
                else:
                    data = response.json()
                
                # Prendiamo l'estrazione più recente
                ultima = data[0] if isinstance(data, list) else data
                
                # Normalizziamo le ruote (Iniziale Maiuscola)
                ruote_pulite = {k.capitalize(): v for k, v in ultima["ruote"].items()}
                
                return {
                    "data": ultima.get("data", datetime.now().strftime("%d/%m/%Y")),
                    "ruote": ruote_pulite
                }
        except Exception as e:
            print(f"Salto fonte {url} per errore: {e}")
            continue
    return None

def update():
    print("Inizio recupero dati da Dataset Open Source...")
    dati = get_data_open_source()
    filename = 'estrazioni.json'
    
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                db = json.load(f)
            except:
                db = {"lotto": [], "superenalotto": [], "last_global_update": ""}
    else:
        db = {"lotto": [], "superenalotto": [], "last_global_update": ""}

    if dati and dati.get("ruote"):
        # Verifichiamo se l'estrazione è nuova
        ultima_data_salvata = db["lotto"][0]["data"] if db["lotto"] else ""
        
        if dati["data"] != ultima_data_salvata:
            db["lotto"].insert(0, dati)
            db["lotto"] = db["lotto"][:30] # Teniamo uno storico più lungo
            db["last_global_update"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=4, ensure_ascii=False)
            print(f"✅ SUCCESSO! Dati recuperati correttamente per il {dati['data']}")
        else:
            print("ℹ️ Il file è già aggiornato all'ultima estrazione disponibile.")
    else:
        print("❌ Anche i Dataset Open Source hanno fallito o sono vuoti.")

if __name__ == "__main__":
    update()
