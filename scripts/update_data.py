import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_real_data():
    database = {"lotto": [], "superenalotto": [], "last_global_update": ""}
    
    try:
        # --- SCRAPING LOTTO ---
        url_lotto = "https://www.estrazionedellotto.it/ultime-estrazioni-del-lotto.asp"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res_lotto = requests.get(url_lotto, headers=headers)
        soup_lotto = BeautifulSoup(res_lotto.text, 'html.parser')

        lotto_entry = {"data": "", "ruote": {}}
        
        # Cerchiamo la data
        data_tag = soup_lotto.find("span", {"class": "data-estrazione"})
        lotto_entry["data"] = data_tag.text.strip() if data_tag else datetime.now().strftime("%d/%m/%Y")

        # Cerchiamo le ruote nella tabella
        table = soup_lotto.find("table", {"class": "tabella-estrazioni"})
        if table:
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 6:
                    nome_ruota = cols[0].text.strip()
                    numeri = [int(cols[i].text.strip()) for i in range(1, 6)]
                    lotto_entry["ruote"][nome_ruota] = numeri
        
        database["lotto"].append(lotto_entry)

        # --- SCRAPING SUPERENALOTTO ---
        url_super = "https://www.estrazionedellotto.it/ultime-estrazioni-superenalotto.asp"
        res_super = requests.get(url_super, headers=headers)
        soup_super = BeautifulSoup(res_super.text, 'html.parser')
        
        super_entry = {"data": lotto_entry["data"], "numeri": [], "jolly": 0, "superstar": 0}
        
        # Cerchiamo i 6 numeri principali
        palle = soup_super.find_all("span", {"class": "palla-superenalotto"})
        if len(palle) >= 6:
            super_entry["numeri"] = [int(palle[i].text.strip()) for i in range(6)]
            
        # Jolly e Superstar
        jolly_tag = soup_super.find("span", {"class": "palla-jolly"})
        if jolly_tag: super_entry["jolly"] = int(jolly_tag.text.strip())
        
        star_tag = soup_super.find("span", {"class": "palla-superstar"})
        if star_tag: super_entry["superstar"] = int(star_tag.text.strip())

        database["superenalotto"].append(super_entry)
        
        database["last_global_update"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        return database

    except Exception as e:
        print(f"Errore: {e}")
        return None

def update():
    newData = get_real_data()
    if newData and len(newData["lotto"][0]["ruote"]) > 0:
        with open('estrazioni.json', 'w') as f:
            json.dump(newData, f, indent=4)
        print("Dati reali scaricati e salvati!")

if __name__ == "__main__":
    update()
