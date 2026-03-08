import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_lotto_api():
    url = "https://lotto-api.onrender.com/lotto/latest"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            api_data = response.json()
            ruote_mappa = {
                "bari": "Bari", "cagliari": "Cagliari", "firenze": "Firenze",
                "genova": "Genova", "milano": "Milano", "napoli": "Napoli",
                "palermo": "Palermo", "roma": "Roma", "torino": "Torino",
                "venezia": "Venezia", "nazionale": "Nazionale"
            }
            lotto_entry = {
                "data": api_data.get("date", datetime.now().strftime("%d/%m/%Y")),
                "ruote": {}
            }
            for key, beauty_name in ruote_mappa.items():
                if key in api_data:
                    lotto_entry["ruote"][beauty_name] = api_data[key]
            return lotto_entry
    except:
        return None

def get_superenalotto_scraping():
    url = "https://www.estrazionedellotto.it/ultime-estrazioni-superenalotto.asp"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        palle = soup.select(".palla-superenalotto")
        numeri = [int(p.text.strip()) for p in palle[:6] if p.text.strip().isdigit()]
        
        jolly = soup.find("span", class_="palla-jolly")
        star = soup.find("span", class_="palla-superstar")
        
        return {
            "data": datetime.now().strftime("%d/%m/%Y"),
            "numeri": numeri,
            "jolly": int(jolly.text) if jolly else 0,
            "superstar": int(star.text) if star else 0
        }
    except:
        return {"data": "", "numeri": [], "jolly": 0, "superstar": 0}

def update():
    lotto = get_lotto_api()
    super_e = get_superenalotto_scraping()
    
    if lotto and lotto["ruote"]:
        try:
            with open('estrazioni.json', 'r', encoding='utf-8') as f:
                db = json.load(f)
        except:
            db = {"lotto": [], "superenalotto": []}

        # Aggiorna Lotto
        if not db["lotto"] or lotto["data"] != db["lotto"][0]["data"]:
            db["lotto"].insert(0, lotto)
            db["lotto"] = db["lotto"][:20]

        # Aggiorna Superenalotto
        if super_e["numeri"]:
            if not db["superenalotto"] or super_e["data"] != db["superenalotto"][0]["data"]:
                db["superenalotto"].insert(0, super_e)
                db["superenalotto"] = db["superenalotto"][:20]

        db["last_global_update"] = datetime.now().strftime("%d/%m/%Y %H:%M")

        with open('estrazioni.json', 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print("DATABASE AGGIORNATO CON SUCCESSO!")
    else:
        print("ERRORE: Dati Lotto non recuperati.")

if __name__ == "__main__":
    update()
