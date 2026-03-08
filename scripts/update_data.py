import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_real_data():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        # 1. ESTRAZIONE LOTTO
        url_lotto = "https://www.estrazionedellotto.it/ultime-estrazioni-del-lotto.asp"
        res = requests.get(url_lotto, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')

        lotto_entry = {"data": "", "ruote": {}}
        
        # Cerchiamo la data
        data_tag = soup.find("span", class_="data-estrazione")
        lotto_entry["data"] = data_tag.get_text(strip=True) if data_tag else datetime.now().strftime("%d/%m/%Y")

        # Cerchiamo TUTTE le tabelle e troviamo quella che contiene le ruote
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 6:
                    nome = cols[0].get_text(strip=True).capitalize()
                    lista_ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano", "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]
                    if nome in lista_ruote:
                        # Estraiamo i 5 numeri reali
                        numeri = [int(cols[i].get_text(strip=True)) for i in range(1, 6)]
                        lotto_entry["ruote"][nome] = numeri

        # 2. ESTRAZIONE SUPERENALOTTO
        url_super = "https://www.estrazionedellotto.it/ultime-estrazioni-superenalotto.asp"
        res_s = requests.get(url_super, headers=headers, timeout=10)
        soup_s = BeautifulSoup(res_s.text, 'html.parser')
        
        super_entry = {"data": lotto_entry["data"], "numeri": [], "jolly": 0, "superstar": 0}
        palle = soup_s.select(".palla-superenalotto, .palla-otto") # Cerca entrambe le classi possibili
        
        numeri_estratti = [int(p.get_text(strip=True)) for p in palle if p.get_text(strip=True).isdigit()]
        if len(numeri_estratti) >= 6:
            super_entry["numeri"] = numeri_estratti[:6]
            
        database = {
            "lotto": [lotto_entry],
            "superenalotto": [super_entry],
            "last_global_update": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        return database
    except Exception as e:
        print(f"ERRORE REALE: {e}")
        return None

def update():
    newData = get_real_data()
    # Verifichiamo che abbiamo almeno una ruota (es. Bari) prima di salvare
    if newData and len(newData["lotto"][0]["ruote"]) > 0:
        with open('estrazioni.json', 'w', encoding='utf-8') as f:
            json.dump(newData, f, indent=4, ensure_ascii=False)
        print("OK: Dati reali salvati correttamente!")
    else:
        print("ERRORE: Lo script non ha trovato i numeri sul sito.")

if __name__ == "__main__":
    update()
