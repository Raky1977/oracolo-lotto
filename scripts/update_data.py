import json
import requests
from datetime import datetime
import os

def get_data_lotto():
    # Usiamo un endpoint che restituisce dati più facilmente digeribili
    # Questa URL punta a un servizio di risultati che non blocca GitHub
    url = "https://www.estrazionedellotto.it/res/lotto.json" # Esempio di risorsa JSON
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.estrazionedellotto.it/'
    }
    
    try:
        # Tentativo 1: API/JSON diretto
        # Se questo URL specifico fallisce, usiamo un fallback su un altro aggregatore
        response = requests.get("https://raw.githubusercontent.com/fede-94/lotto-italia/main/lotto.json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Adattiamo il formato dell'API al tuo formato JSON
            estrazione = {"data": data[0]["data"], "ruote": data[0]["ruote"]}
            return estrazione
    except:
        pass
    
    # Tentativo 2: Emergenza - Scraping leggero su sito meno protetto
    try:
        url_alt = "https://www.lottologia.com/lotto/ultime-estrazioni/"
        res = requests.get(url_alt, headers=headers, timeout=10)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res.text, 'html.parser')
        
        nuova = {"data": datetime.now().strftime("%d/%m/%Y"), "ruote": {}}
        ruote_nomi = ["Bari", "Cagliari", "Firenze", "Genova", "Milano", "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]
        
        table = soup.find("table")
        if table:
            for row in table.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 6:
                    nome = cols[0].get_text(strip=True).capitalize()
                    if nome in ruote_nomi:
                        nuova["ruote"][nome] = [int(cols[i].get_text(strip=True)) for i in range(1, 6)]
            return nuova
    except:
        return None

def update():
    print("Recupero dati in corso da fonti alternative...")
    dati = get_data_lotto()
    filename = 'estrazioni.json'
    
    # Caricamento db
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try: db = json.load(f)
            except: db = {"lotto": [], "superenalotto": [], "last_global_update": ""}
    else:
        db = {"lotto": [], "superenalotto": [], "last_global_update": ""}

    if dati and dati.get("ruote"):
        # Verifichiamo se l'estrazione è nuova
        ultima_data = db["lotto"][0]["data"] if db["lotto"] else ""
        
        if dati["data"] != ultima_data:
            db["lotto"].insert(0, dati)
            db["lotto"] = db["lotto"][:20]
            db["last_global_update"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=4, ensure_ascii=False)
            print(f"✅ SUCCESSO: Dati aggiornati al {dati['data']}")
        else:
            print("ℹ️ Dati già aggiornati all'ultima estrazione.")
    else:
        print("❌ ERRORE: Nessuna fonte disponibile. Controllo connessione...")

if __name__ == "__main__":
    update()
