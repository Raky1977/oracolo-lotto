import json
import requests
from datetime import datetime
import os

def get_data_open_source():
    # Usiamo un'API affidabile o un repository specchio
    urls = [
        "https://raw.githubusercontent.com/fede-94/lotto-italia/main/lotto.json"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                ultima = data[0] if isinstance(data, list) else data
                return ultima
        except Exception as e:
            print(f"Errore fonte {url}: {e}")
            continue
    return None

def update_txt_file(nuova_estrazione):
    filename = 'storico01-oggi.txt'
    data_estrazione = nuova_estrazione["data"].replace("-", "/") # Normalizza data
    
    # Mappa sigle per il file TXT
    mappa_sigle = {
        "Bari": "BA", "Cagliari": "CA", "Firenze": "FI", "Genova": "GE",
        "Milano": "MI", "Napoli": "NA", "Palermo": "PA", "Roma": "RM",
        "Torino": "TO", "Venezia": "VE", "Nazionale": "RN"
    }

    nuove_righe = []
    for nome_esteso, sigla in mappa_sigle.items():
        # Cerca la ruota nei dati (gestisce maiuscole/minuscole)
        numeri = nuova_estrazione["ruote"].get(nome_esteso) or nuova_estrazione["ruote"].get(nome_esteso.lower())
        if numeri:
            numeri_str = "\t".join(map(str, numeri))
            riga = f"{data_estrazione}\t{sigla}\t{numeri_str}\n"
            nuove_righe.append(riga)

    if not nuove_righe:
        return False

    # Leggi il vecchio contenuto
    with open(filename, 'r', encoding='utf-8') as f:
        vecchio_contenuto = f.read()

    # Verifica se la data è già presente per evitare duplicati
    if data_estrazione in vecchio_contenuto[:500]: # Controlla solo l'inizio del file
        print(f"Dati del {data_estrazione} già presenti nel TXT.")
        return False

    # Scrivi le nuove righe in cima
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(nuove_righe)
        f.write(vecchio_contenuto)
    return True

def run():
    print("Recupero dati...")
    dati = get_data_open_source()
    if dati:
        if update_txt_file(dati):
            print("✅ File TXT aggiornato con successo!")
        else:
            print("ℹ️ Nessun aggiornamento necessario.")
    else:
        print("❌ Impossibile recuperare i dati.")

if __name__ == "__main__":
    run()
