import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_real_data():
    # User agent più comune per evitare blocchi
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        # 1. LOTTO - Usiamo la pagina concorsi per maggiore stabilità
        url_lotto = "https://www.estrazionedellotto.it/"
        res = requests.get(url_lotto, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')

        lotto_entry = {"data": "", "ruote": {}}
        
        # Cerchiamo la data nel primo box disponibile
        data_tag = soup.find("span", class_="data-estrazione")
        lotto_entry["data"] = data_tag.get_text(strip=True) if data_tag else datetime.now().strftime("%d/%m/%Y")

        # Cerchiamo tutte le righe che contengono i nomi delle ruote
        # Molte volte sono in div con classe 'riga-estrazione' o tabelle standard
        rows = soup.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 6:
                nome_raw = cols[0].get_text(strip=True).capitalize()
                # Pulizia nomi per match perfetto con lo Spinner dell'app
                lista_valida = ["Bari", "Cagliari", "Firenze", "Genova", "Milano", "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]
                if nome_raw in lista_valida:
                    try:
                        numeri = [int(cols[i].get_text(strip=True)) for i in range(1, 6)]
                        lotto_entry["ruote"][nome_raw] = numeri
                    except:
                        continue

        # 2. SUPERENALOTTO
        super_entry = {"data": lotto_entry["data"], "numeri": [], "jolly": 0, "superstar": 0}
        # Cerchiamo i numeri nelle palle colorate
        palle = soup.select(".palla-superenalotto, .palla-otto, .ball")
        numeri_s = []
        for p in palle:
            txt = p.get_text(strip=True)
            if txt.isdigit():
                numeri_s.append(int(txt))
        
        if len(numeri_s) >= 6:
            super_entry["numeri"] = numeri_s[:6]
            if len(numeri_s) >= 7: super_entry["jolly"] = numeri_s[6]
            if len(numeri_s) >= 8: super_entry["superstar"] = numeri_s[7]

        return {
            "lotto": [lotto_entry],
            "superenalotto": [super_entry],
            "last_global_update": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
    except Exception as e:
        print(f"Errore durante lo scraping: {e}")
        return None

def update():
    newData = get_real_data()
    # SALVATAGGIO FORZATO: se abbiamo i dati, scriviamo.
    if newData and len(newData["lotto"][0]["ruote"]) > 0:
        with open('estrazioni.json', 'w', encoding='utf-8') as f:
            json.dump(newData, f, indent=4, ensure_ascii=False)
        print("SUCCESSO: Dati scritti nel JSON")
    else:
        print("FALLIMENTO: Nessun dato trovato, non sovrascrivo per evitare di svuotare il file")

if __name__ == "__main__":
    update()
