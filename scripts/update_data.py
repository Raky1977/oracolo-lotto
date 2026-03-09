import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_real_data():
    # Usiamo una testata giornalistica, molto più stabile e veloce
    url = "https://www.corriere.it/estrazioni-lotto-superenalotto/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        lotto_entry = {"data": datetime.now().strftime("%d/%m/%Y"), "ruote": {}}
        
        # Cerchiamo le ruote nelle tabelle del Corriere
        # Il Corriere usa classi molto semplici per le tabelle
        tables = soup.find_all("table")
        for table in tables:
            for row in table.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 6:
                    nome = cols[0].get_text(strip=True).capitalize()
                    lista_ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano", "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]
                    if nome in lista_ruote:
                        # Prendiamo i 5 numeri
                        numeri = [int(cols[i].get_text(strip=True)) for i in range(1, 6) if cols[i].get_text(strip=True).isdigit()]
                        if len(numeri) == 5:
                            lotto_entry["ruote"][nome] = numeri

        # Superenalotto
        super_entry = {"data": lotto_entry["data"], "numeri": [], "jolly": 0, "superstar": 0}
        # Cerchiamo i numeri del superenalotto (spesso in div circolari)
        palle = soup.find_all("span", class_="ball") # Classe comune per i numeri del superenalotto
        if not palle:
            palle = soup.select(".num-superenalotto") # Alternativa
            
        numeri_s = [int(p.get_text(strip=True)) for p in palle if p.get_text(strip=True).isdigit()]
        if len(numeri_s) >= 6:
            super_entry["numeri"] = numeri_s[:6]
            if len(numeri_s) >= 7: super_entry["jolly"] = numeri_s[6]

        if not lotto_entry["ruote"]:
            return None

        return {
            "lotto": [lotto_entry],
            "superenalotto": [super_entry],
            "last_global_update": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
    except Exception as e:
        print(f"Errore tecnico: {e}")
        return None

def update():
    newData = get_real_data()
    if newData:
        # Carichiamo lo storico per non perderlo
        try:
            with open('estrazioni.json', 'r', encoding='utf-8') as f:
                db = json.load(f)
        except:
            db = {"lotto": [], "superenalotto": []}

        # Inseriamo i nuovi dati solo se la data è diversa
        if not db["lotto"] or newData["lotto"][0]["data"] != db["lotto"][0]["data"]:
            db["lotto"].insert(0, newData["lotto"][0])
            db["superenalotto"].insert(0, newData["superenalotto"][0])
            db["lotto"] = db["lotto"][:30] # Teniamo 30 estrazioni
            db["superenalotto"] = db["superenalotto"][:30]
            
        db["last_global_update"] = newData["last_global_update"]

        with open('estrazioni.json', 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print("OK: File aggiornato con dati Corriere.")
    else:
        print("KO: Dati non trovati sulla fonte.")

if __name__ == "__main__":
    update()
