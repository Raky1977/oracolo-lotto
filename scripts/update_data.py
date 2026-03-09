import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

def get_data_with_proxy():
    # Usiamo un servizio di proxy free-tier per nascondere l'IP di GitHub
    # Questo URL agisce da "ponte"
    target_url = "https://www.estrazionedellotto.it/ultime-estrazioni-del-lotto.asp"
    
    # Usiamo un proxy pubblico o un servizio di rotazione (es. ScraperAPI o similari)
    # Per ora proviamo con un proxy trasparente e User-Agent rotativo
    proxy_url = f"https://api.allorigins.win/get?url={target_url}"
    
    print(f"Tentativo di accesso tramite tunnel a: {target_url}")
    
    try:
        response = requests.get(proxy_url, timeout=20)
        if response.status_code == 200:
            # AllOrigins restituisce un JSON con il contenuto HTML dentro 'contents'
            raw_html = response.json().get('contents', '')
            soup = BeautifulSoup(raw_html, 'html.parser')
            
            nuova = {"data": datetime.now().strftime("%d/%m/%Y"), "ruote": {}}
            ruote_nomi = ["Bari", "Cagliari", "Firenze", "Genova", "Milano", "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]
            
            rows = soup.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 6:
                    nome = cols[0].get_text(strip=True).capitalize()
                    if nome in ruote_nomi:
                        numeri = [int(cols[i].get_text(strip=True)) for i in range(1, 6) if cols[i].get_text(strip=True).isdigit()]
                        if len(numeri) == 5:
                            nuova["ruote"][nome] = numeri
            
            return nuova if nuova["ruote"] else None
    except Exception as e:
        print(f"Errore durante il passaggio nel tunnel: {e}")
        return None

def update():
    print("Avvio recupero dati con sistema Proxy...")
    dati = get_data_with_proxy()
    filename = 'estrazioni.json'
    
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try: db = json.load(f)
            except: db = {"lotto": [], "superenalotto": [], "last_global_update": ""}
    else:
        db = {"lotto": [], "superenalotto": [], "last_global_update": ""}

    if dati and len(dati["ruote"]) > 0:
        ultima_data = db["lotto"][0]["data"] if db["lotto"] else ""
        if dati["data"] != ultima_data:
            db["lotto"].insert(0, dati)
            db["lotto"] = db["lotto"][:20]
            db["last_global_update"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=4, ensure_ascii=False)
            print(f"✅ BINGO! Dati estratti e salvati tramite Proxy per il {dati['data']}")
        else:
            print("ℹ️ Dati già presenti, nulla da aggiornare.")
    else:
        print("❌ Anche il sistema Proxy è stato respinto dal sito.")

if __name__ == "__main__":
    update()
