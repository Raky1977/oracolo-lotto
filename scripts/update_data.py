import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_data():
    # Fonte stabile: Estrazioni del Lotto (Sisal o simili)
    url = "https://www.estrazionedellotto.it/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        res = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Prepariamo l'estrazione di oggi
        data_estrazione = datetime.now().strftime("%d/%m/%Y")
        nuova_estrazione = {"data": data_estrazione, "ruote": {}}
        
        # Cerchiamo le ruote
        ruote_nomi = ["Bari", "Cagliari", "Firenze", "Genova", "Milano", "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]
        
        rows = soup.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 6:
                nome = cols[0].get_text(strip=True).capitalize()
                if nome in ruote_nomi:
                    numeri = [int(cols[i].get_text(strip=True)) for i in range(1, 6) if cols[i].get_text(strip=True).isdigit()]
                    if len(numeri) == 5:
                        nuova_estrazione["ruote"][nome] = numeri

        if not nuova_estrazione["ruote"]:
            return None

        return nueva_estrazione
    except Exception as e:
        print(f"Errore Scraping: {e}")
        return None

def update():
    nuovi_dati = get_data()
    if nuovi_dati:
        # TENTATIVO DI LETTURA SICURO
        try:
            with open('estrazioni.json', 'r', encoding='utf-8') as f:
                content = f.read().strip()
                db = json.loads(content) if content else {"lotto": [], "superenalotto": []}
        except Exception:
            db = {"lotto": [], "superenalotto": []}

        # Aggiungiamo i dati se la data è nuova
        if not db["lotto"] or nuovi_dati["data"] != db["lotto"][0]["data"]:
            db["lotto"].insert(0, nuovi_dati)
            db["lotto"] = db["lotto"][:20]
            db["last_global_update"] = datetime.now().strftime("%d/%m/%Y %H:%M")

            with open('estrazioni.json', 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=4, ensure_ascii=False)
            print("Aggiornamento completato con successo.")
        else:
            print("Dati già presenti per oggi.")
    else:
        print("Nessun dato trovato sul sito.")

if __name__ == "__main__":
    update()
