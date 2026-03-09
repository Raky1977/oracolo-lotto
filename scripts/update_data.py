import json
import requests
from datetime import datetime
import os

def get_data_sisal():
    # Sisal è il gestore ufficiale, meno probabile che dia 404
    # Usiamo un URL che punta direttamente all'ultima estrazione
    url = "https://www.sisal.it/api-risultati-giochi/v2/estrazioni/LOTTO/ultime-estrazioni"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # Prendiamo il primo concorso (il più recente)
            concorso = data[0]
            data_est = concorso.get("dataEstrazione", datetime.now().strftime("%d/%m/%Y"))
            
            estrazione_pulita = {"data": data_est, "ruote": {}}
            
            # Mappiamo i risultati sulle ruote
            for dettaglio in concorso.get("dettagli", []):
                ruota_nome = dettaglio.get("ruota", "").capitalize()
                numeri = dettaglio.get("numeri", [])
                if ruota_nome and numeri:
                    estrazione_pulita["ruote"][ruota_nome] = numeri
            
            return estrazione_pulita
    except Exception as e:
        print(f"Errore Sisal: {e}")
    return None

def update():
    print("Recupero dati ufficiali da Sisal...")
    dati = get_data_sisal()
    filename = 'estrazioni.json'
    
    # Gestione file JSON
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try: db = json.load(f)
            except: db = {"lotto": [], "superenalotto": [], "last_global_update": ""}
    else:
        db = {"lotto": [], "superenalotto": [], "last_global_update": ""}

    if dati and dati["ruote"]:
        ultima_data = db["lotto"][0]["data"] if db["lotto"] else ""
        
        if dati["data"] != ultima_data:
            db["lotto"].insert(0, dati)
            db["lotto"] = db["lotto"][:20]
            db["last_global_update"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=4, ensure_ascii=False)
            print(f"✅ SUCCESSO: Dati reali Sisal salvati per il {dati['data']}")
        else:
            print("ℹ️ Già aggiornato.")
    else:
        print("❌ Fallimento: Sisal non ha restituito dati.")

if __name__ == "__main__":
    update()
