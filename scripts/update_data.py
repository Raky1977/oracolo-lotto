import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

def get_data_fonte_1():
    """Prova a leggere da un sito di risultati rapido"""
    url = "https://www.estrazionedellotto.it/ultime-estrazioni-del-lotto.asp"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        estrazione = {"data": datetime.now().strftime("%d/%m/%Y"), "ruote": {}}
        
        ruote_target = ["Bari", "Cagliari", "Firenze", "Genova", "Milano", "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]
        
        # Cerca i dati nelle righe della tabella
        rows = soup.find_all("tr")
        for row in rows:
            tds = row.find_all("td")
            if len(tds) >= 6:
                nome = tds[0].get_text(strip=True).capitalize()
                if nome in ruote_target:
                    numeri = [int(tds[i].get_text(strip=True)) for i in range(1, 6) if tds[i].get_text(strip=True).isdigit()]
                    if len(numeri) == 5:
                        estrazione["ruote"][nome] = numeri
        
        return estrazione if len(estrazione["ruote"]) > 5 else None
    except:
        return None

def get_data_fonte_backup():
    """Fonte di emergenza se la prima fallisce"""
    # Placeholder per una seconda fonte (es. API o altro sito)
    return None

def update():
    print("Inizio recupero dati...")
    dati = get_data_fonte_1()
    
    if not dati:
        print("Fonte 1 fallita, provo fonte backup...")
        dati = get_data_fonte_backup()

    filename = 'estrazioni.json'
    
    # Caricamento database attuale
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                db = json.load(f)
            except:
                db = {"lotto": [], "superenalotto": [], "last_global_update": ""}
    else:
        db = {"lotto": [], "superenalotto": [], "last_global_update": ""}

    if dati and dati["ruote"]:
        # Controlla se l'estrazione è già presente
        ultima_data = db["lotto"][0]["data"] if db["lotto"] else ""
        
        if dati["data"] != ultima_data:
            db["lotto"].insert(0, dati)
            db["lotto"] = db["lotto"][:20] # Teniamo le ultime 20
            db["last_global_update"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=4, ensure_ascii=False)
            print(f"SUCCESSO: Dati salvati per il {dati['data']}")
        else:
            print("Dati già aggiornati. Nessuna modifica necessaria.")
    else:
        print("ERRORE CRITICO: Nessuna fonte ha restituito dati validi.")
        # Se vogliamo forzare un riempimento per test, togli il commento qui sotto:
        # db["last_global_update"] = "TEST FALLITO - " + datetime.now().strftime("%H:%M")
        # with open(filename, 'w') as f: json.dump(db, f)

if __name__ == "__main__":
    update()
