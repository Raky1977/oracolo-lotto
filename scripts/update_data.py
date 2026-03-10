import json
import requests
from datetime import datetime
import os

def get_data_backup():
    # Fonti multiple per massima sicurezza
    urls = [
        "https://raw.githubusercontent.com/fede-94/lotto-italia/main/lotto.json",
        "https://api.allorigins.win/get?url=https://www.estrazionedellotto.it/res/lotto.json",
        "https://raw.githubusercontent.com/michele-v/lotto-italia/master/lotto.json"
    ]
    
    for url in urls:
        try:
            print(f"Tentativo su: {url}")
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                content = response.json()
                # Gestione wrapper AllOrigins
                if "contents" in content:
                    data = json.loads(content["contents"])
                else:
                    data = content
                
                ultima = data[0] if isinstance(data, list) else data
                if "ruote" in ultima:
                    print(f"✅ Dati trovati per la data: {ultima.get('data')}")
                    return ultima
        except Exception as e:
            print(f"Fonte fallita: {url} - Errore: {e}")
            continue
    return None

def update_txt_file(nuova_estrazione):
    filename = 'storico01-oggi.txt'
    # Pulizia data: trasforma "03-03-2026" o simili in "2026/03/03"
    raw_data = nuova_estrazione["data"].replace("-", "/")
    # Se la data è GG/MM/AAAA la giriamo per il tuo file
    parti_data = raw_data.split("/")
    if len(parti_data[0]) == 2: # è nel formato 03/03/2026
        data_estrazione = f"{parti_data[2]}/{parti_data[1]}/{parti_data[0]}"
    else:
        data_estrazione = raw_data

    mappa_sigle = {
        "Bari": "BA", "Cagliari": "CA", "Firenze": "FI", "Genova": "GE",
        "Milano": "MI", "Napoli": "NA", "Palermo": "PA", "Roma": "RM",
        "Torino": "TO", "Venezia": "VE", "Nazionale": "RN"
    }

    nuove_righe = []
    # Gestiamo sia chiavi Maiuscole che minuscole
    ruote_data = {k.capitalize(): v for k, v in nuova_estrazione["ruote"].items()}

    for nome_esteso, sigla in mappa_sigle.items():
        numeri = ruote_data.get(nome_esteso)
        if numeri:
            numeri_str = "\t".join(map(str, numeri))
            riga = f"{data_estrazione}\t{sigla}\t{numeri_str}\n"
            nuove_righe.append(riga)

    if not nuove_righe:
        print("❌ Errore: Nessuna ruota trovata nei dati scaricati.")
        return False

    with open(filename, 'r', encoding='utf-8') as f:
        vecchio_contenuto = f.read()

    if data_estrazione in vecchio_contenuto[:1000]:
        print(f"ℹ️ Dati del {data_estrazione} già presenti. Esco.")
        return False

    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(nuove_righe)
        f.write(vecchio_contenuto)
    return True

if __name__ == "__main__":
    dati = get_data_backup()
    if dati and update_txt_file(dati):
        print("🚀 UPDATE COMPLETATO!")
    else:
        print("⚠️ Nessun aggiornamento effettuato.")
