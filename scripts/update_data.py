import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_real_data():
    database = {"lotto": [], "superenalotto": [], "last_global_update": ""}
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # Estrazione Lotto
        url_lotto = "https://www.estrazionedellotto.it/ultime-estrazioni-del-lotto.asp"
        res_lotto = requests.get(url_lotto, headers=headers)
        soup_lotto = BeautifulSoup(res_lotto.text, 'html.parser')

        lotto_entry = {"data": "", "ruote": {}}
        data_tag = soup_lotto.find("span", {"class": "data-estrazione"})
        lotto_entry["data"] = data_tag.text.strip() if data_tag else datetime.now().strftime("%d/%m/%Y")

        table = soup_lotto.find("table", {"class": "tabella-estrazioni"})
        if table:
            for row in table.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 6:
                    nome_ruota = cols[0].text.strip().capitalize()
                    if nome_ruota in ["Bari", "Cagliari", "Firenze", "Genova", "Milano", "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]:
                        lotto_entry["ruote"][nome_ruota] = [int(cols[i].text.strip()) for i in range(1, 6)]
        
        database["lotto"].append(lotto_entry)

        # Estrazione Superenalotto
        url_super = "https://www.estrazionedellotto.it/ultime-estrazioni-superenalotto.asp"
        res_super = requests.get(url_super, headers=headers)
        soup_super = BeautifulSoup(res_super.text, 'html.parser')
        
        super_entry = {"data": lotto_entry["data"], "numeri": [], "jolly": 0, "superstar": 0}
        palle = soup_super.select(".palla-superenalotto")
        if len(palle) >= 6:
            super_entry["numeri"] = [int(palle[i].text.strip()) for i in range(6)]
        
        database["superenalotto"].append(super_entry)
        database["last_global_update"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        return database
    except Exception as e:
        print(f"Errore: {e}")
        return None

def update():
    newData = get_real_data()
    if newData:
        with open('estrazioni.json', 'w') as f:
            json.dump(newData, f, indent=4)
        print("Dati reali scritti nel file!")

if __name__ == "__main__":
    update()
