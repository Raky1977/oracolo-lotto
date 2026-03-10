import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import os

def scrape_lotto():
    url = "https://www.estrazionilottooggi.it/"
    # User-Agent più completo per simulare un browser reale
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        print(f"Connessione a: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"Errore HTTP: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Trova la Data
        # Il sito usa spesso un tag h1 o h2 per la data principale
        testo_pagina = soup.get_text()
        data_match = re.search(r'(\d{2}/\d{2}/\d{4})', testo_pagina)
        if not data_match:
            print("Impossibile trovare la data nella pagina.")
            return None
        
        data_gg_mm_aaaa = data_match.group(1)
        d = datetime.strptime(data_gg_mm_aaaa, "%d/%m/%Y")
        data_formattata = d.strftime("%Y/%m/%d")
        print(f"Data rilevata sul sito: {data_formattata}")

        # 2. Estrazione Ruote e Numeri
        # Cerchiamo i blocchi che contengono il nome della ruota e i 5 numeri
        ruote_nomi = ["Bari", "Cagliari", "Firenze", "Genova", "Milano", "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]
        risultato = {"data": data_formattata, "ruote": {}}

        # Cerchiamo tutte le righe o i blocchi di testo
        for r in ruote_nomi:
            # Cerchiamo il nome della ruota nel testo e proviamo a prendere i numeri successivi
            # Spesso i numeri sono in elementi con classe "num" o dentro una cella td
            elemento_ruota = soup.find(text=re.compile(r, re.IGNORECASE))
            if elemento_ruota:
                parent = elemento_ruota.find_parent(['tr', 'div'])
                # Estraiamo tutti i numeri dal contenitore della ruota
                numeri = re.findall(r'\b(\d{1,2})\b', parent.get_text())
                # Filtriamo solo i primi 5 numeri validi (1-90)
                numeri_puliti = [int(n) for n in numeri if 1 <= int(n) <= 90][:5]
                
                if len(numeri_puliti) == 5:
                    risultato["ruote"][r] = numeri_puliti
                    print(f"Presa ruota {r}: {numeri_puliti}")

        if len(risultato["ruote"]) < 11:
            print(f"Attenzione: Trovate solo {len(risultato['ruote'])} ruote su 11.")
        
        return risultato if len(risultato["ruote"]) > 0 else None

    except Exception as e:
        print(f"Errore durante lo scraping: {e}")
        return None

def update_txt(nuova):
    filename = 'storico01-oggi.txt'
    if not nuova: return False

    # Mappa sigle per il tuo file .txt
    mappa_sigle = {
        "Bari": "BA", "Cagliari": "CA", "Firenze": "FI", "Genova": "GE",
        "Milano": "MI", "Napoli": "NA", "Palermo": "PA", "Roma": "RM",
        "Torino": "TO", "Venezia": "VE", "Nazionale": "RN"
    }

    if not os.path.exists(filename):
        print(f"Errore: {filename} non trovato!")
        return False

    with open(filename, 'r', encoding='utf-8') as f:
        vecchio_contenuto = f.read()

    if nuova["data"] in vecchio_contenuto[:500]:
        print(f"L'estrazione del {nuova['data']} è già presente nel file.")
        return False

    nuove_righe = ""
    for nome, sigla in mappa_sigle.items():
        numeri = nuova["ruote"].get(nome)
        if numeri:
            nuove_righe += f"{nuova['data']}\t{sigla}\t" + "\t".join(map(str, numeri)) + "\n"

    if nuove_righe:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(nuove_righe + vecchio_contenuto)
        return True
    return False

if __name__ == "__main__":
    dati = scrape_lotto()
    if dati and update_txt(dati):
        print("✅ AGGIORNAMENTO COMPLETATO CON SUCCESSO!")
    else:
        print("❌ Nessuna modifica apportata.")
