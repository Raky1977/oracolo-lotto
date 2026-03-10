import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

def scrape_lotto_oggi():
    url = "https://www.estrazionilottooggi.it/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        print(f"Scraping da: {url}")
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Cerchiamo la data dell'estrazione
        # Di solito è in un tag h2 o simile (es: "Estrazione del 03/03/2026")
        data_testo = soup.find("h2").get_text() 
        # Estraiamo solo la data GG/MM/AAAA
        import re
        data_match = re.search(r'(\d{2}/\d{2}/\d{4})', data_testo)
        if not data_match:
            return None
        
        data_gg_mm_aaaa = data_match.group(1)
        # Convertiamo in AAAA/MM/GG per il tuo file .txt
        d = datetime.strptime(data_gg_mm_aaaa, "%d/%m/%Y")
        data_formattata = d.strftime("%Y/%m/%p").replace("AM","").replace("PM","").strip() # Gestione locale
        data_formattata = d.strftime("%Y/%m/%d")

        ruote_nomi = ["Bari", "Cagliari", "Firenze", "Genova", "Milano", "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]
        estrazione = {"data": data_formattata, "ruote": {}}

        # Lo scraper cerca le tabelle dei numeri
        tabelle = soup.find_all("table")
        for tabella in tabelle:
            rows = tabella.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    nome_ruota = cols[0].get_text(strip=True).capitalize()
                    if nome_ruota in ruote_nomi:
                        # Prende i 5 numeri
                        numeri = [int(n.get_text(strip=True)) for n in cols[1:] if n.get_text(strip=True).isdigit()]
                        if len(numeri) == 5:
                            estrazione["ruote"][nome_ruota] = numeri

        if len(estrazione["ruote"]) >= 11:
            return estrazione
    except Exception as e:
        print(f"Errore Scraping: {e}")
    return None

def update_txt_file(nuova):
    filename = 'storico01-oggi.txt'
    mappa_sigle = {
        "Bari": "BA", "Cagliari": "CA", "Firenze": "FI", "Genova": "GE",
        "Milano": "MI", "Napoli": "NA", "Palermo": "PA", "Roma": "RM",
        "Torino": "TO", "Venezia": "VE", "Nazionale": "RN"
    }

    if not nuova or not nuova["ruote"]: return False

    with open(filename, 'r', encoding='utf-8') as f:
        vecchio_contenuto = f.read()

    if nuova["data"] in vecchio_contenuto[:500]:
        print(f"Data {nuova['data']} già presente.")
        return False

    nuove_righe = ""
    for nome, sigla in mappa_sigle.items():
        numeri = nuova["ruote"].get(nome)
        if numeri:
            nuove_righe += f"{nuova['data']}\t{sigla}\t" + "\t".join(map(str, numeri)) + "\n"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(nuove_righe + vecchio_contenuto)
    return True

if __name__ == "__main__":
    dati = scrape_lotto_oggi()
    if dati and update_txt_file(dati):
        print(f"✅ Aggiornato al {dati['data']}!")
    else:
        print("❌ Nessun nuovo dato trovato.")
