import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_real_data():
    database = {"lotto": [], "superenalotto": [], "last_global_update": ""}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        # --- 1. ESTRAZIONE LOTTO (TUTTE LE RUOTE) ---
        url_lotto = "https://www.estrazionedellotto.it/ultime-estrazioni-del-lotto.asp"
        res_lotto = requests.get(url_lotto, headers=headers)
        soup_lotto = BeautifulSoup(res_lotto.text, 'html.parser')

        lotto_entry = {"data": "", "ruote": {}}
        
        # Trova la data dell'estrazione
        data_tag = soup_lotto.find("span", {"class": "data-estrazione"})
        lotto_entry["data"] = data_tag.text.strip() if data_tag else datetime.now().strftime("%d/%m/%Y")

        # Trova la tabella delle estrazioni
        table = soup_lotto.find("table", {"class": "tabella-estrazioni"})
        if table:
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                # Una riga valida ha il nome ruota + 5 numeri
                if len(cols) >= 6:
                    nome_ruota = cols[0].text.strip().capitalize()
                    # Pulizia nome ruota (es. "10elotto" o nomi sporchi)
                    if nome_ruota in ["Bari", "Cagliari", "Firenze", "Genova", "Milano", "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]:
                        numeri = [int(cols[i].text.strip()) for i in range(1, 6)]
                        lotto_entry["ruote"][nome_ruota] = numeri
        
        database["lotto"].append(lotto_entry)

        # --- 2. ESTRAZIONE SUPERENALOTTO ---
        url_super = "https://www.estrazionedellotto.it/ultime-estrazioni-superenalotto.asp"
        res_super = requests.get(url_super, headers=headers)
        soup_super = BeautifulSoup(res_super.text, 'html.parser')
        
        super_entry = {"data": lotto_entry["data"], "numeri": [], "jolly": 0, "superstar": 0}
        
        # Numeri principali
        palle = soup_super.select(".palla-superenalotto")
        if len(palle) >= 6:
            super_entry["numeri"] = [int(palle[i].text.strip()) for i in range(6)]
            
        # Jolly e Superstar
        j_tag = soup_super.find("span", {"class": "palla-jolly"})
        s_tag = soup_super.find("span", {"class": "palla-superstar"})
        if j_tag: super_entry["jolly"] = int(j_tag.text.strip())
        if s_tag: super_entry["superstar"] = int(s_tag.text.strip())

        database["superenalotto"].append(super_entry)
        
        # Timestamp aggiornamento
        database["last_global_update"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        return database

    except Exception as e:
        print(f"Errore durante lo scraping: {e}")
        return None

def update():
    newData = get_real_data()
    if newData and len(newData["lotto"][0]["ruote"]) > 0:
        # Carichiamo il vecchio database per non perdere lo storico
        try:
            with open('estrazioni.json', 'r') as f:
                old_data = json.load(f)
        except:
            old_data = {"lotto": [], "superenalotto": []}

        # Aggiungiamo i nuovi dati solo se la data è diversa dall'ultima presente
        ultima_data_presente = old_data["lotto"][0]["data"] if old_data["lotto"] else ""
        nuova_data = newData["lotto"][0]["data"]

        if nuova_data != ultima_data_presente:
            # Inseriamo in testa (indice 0) i nuovi dati
            old_data["lotto"].insert(0, newData["lotto"][0])
            old_data["superenalotto"].insert(0, newData["superenalotto"][0])
            # Teniamo solo le ultime 50 estrazioni per non appesantire il file
            old_data["lotto"] = old_data["lotto"][:50]
            old_data["superenalotto"] = old_data["superenalotto"][:50]
        
        old_data["last_global_update"] = newData["last_global_update"]

        with open('estrazioni.json', 'w') as f:
            json.dump(old_data, f, indent=4)
        print("Database aggiornato con successo con dati REALI!")

if __name__ == "__main__":
    update()
