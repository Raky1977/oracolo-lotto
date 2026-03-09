import json
import requests
from datetime import datetime
import os

def get_data_lotto():
    # URL di un'API aperta che fornisce i dati del Lotto in tempo reale
    # Questa fonte è molto più permissiva con GitHub Actions
    url = "https://raw.githubusercontent.com/fede-94/lotto-italia/main/lotto.json"
    
    try:
        print(f"Tentativo di connessione a: {url}")
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            # Prendiamo l'ultima estrazione (la prima dell'elenco)
            ultima = data[0]
            
            # Trasformiamo i nomi delle ruote per farli combaciare con la tua App
            estrazione_pulita = {
                "data": ultima["data"],
                "ruote": {k.capitalize(): v for k, v in ultima["ruote"].items()}
            }
            return estrazione_pulita
        else:
            print(f"Errore server: {response.status_code}")
            return None
    except Exception as e:
        print(f"Errore di rete: {e}")
        return None

def update():
    dati = get_data_lotto()
    filename = 'estrazioni.json'
    
    # Caricamento database attuale o creazione se manca
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                db = json.load(f)
            except:
                db = {"lotto": [], "superenalotto": [], "last_global_update": ""}
    else:
        db = {"lotto": [], "superenalotto": [], "last_global_update": ""}

    if dati:
        # Controlla se abbiamo già questi dati
        ultima_data_salvata = db["lotto"][0]["data"] if db["lotto"] else ""
        
        if dati["data"] != ultima_data_salvata:
            db["lotto"].insert(0, dati)
            db["lotto"] = db["lotto"][:20] # Teniamo lo storico
            db["last_global_update"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=4, ensure_ascii=False)
            print(f"✅ FATTO: Il JSON è stato popolato con i numeri del {dati['data']}")
        else:
            print("ℹ️ Il file è già aggiornato all'ultima estrazione disponibile.")
    else:
        print("❌ Fallimento totale: Anche la fonte API è irraggiungibile.")

if __name__ == "__main__":
    update()
