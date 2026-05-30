import json
import os
import re
from datetime import datetime

mappa_ruote = {
    "BA": "Bari", "CA": "Cagliari", "FI": "Firenze", "GE": "Genova",
    "MI": "Milano", "NA": "Napoli", "PA": "Palermo", "RM": "Roma",
    "TO": "Torino", "VE": "Venezia", "RN": "Nazionale"
}

estrazioni_dict = {}

print("--- AVVIO CONVERTITORE SICURO ---")

if not os.path.exists("storico.txt"):
    print("Errore: storico.txt non trovato!")
    exit(1)

with open("storico.txt", "r", encoding="utf-8") as f:
    for num_riga, riga in enumerate(f, 1):
        riga = riga.strip()
        if not riga:
            continue
            
        # Splitta sia se trova TAB (\t) sia se trova spazi multipli
        parti = re.split(r'\t+|\s+', riga)
        
        if len(parti) < 7:
            # Salta silenziosamente le righe incomplete senza rompere il programma
            continue
            
        data_grezza = parti[0]  # Formato YYYY/MM/DD
        sigla_ruota = parti[1].upper()
        
        try:
            numeri = [int(parti[2]), int(parti[3]), int(parti[4]), int(parti[5]), int(parti[6])]
            data_oggetto = datetime.strptime(data_grezza, "%Y/%m/%d")
            data_formattata = data_oggetto.strftime("%d/%m/%Y")
        except Exception as e:
            # Se una riga è corrotta, la segnala ma continua l'esecuzione!
            print(f"Riga {num_riga} saltata per errore formato: {riga} -> {str(e)}")
            continue
        
        nome_ruota = mappa_ruote.get(sigla_ruota)
        if not nome_ruota:
            continue
            
        if data_formattata not in estrazioni_dict:
            estrazioni_dict[data_formattata] = {
                "data": data_formattata,
                "concorso": "",
                "ruote": {}
            }
            
        estrazioni_dict[data_formattata]["ruote"][nome_ruota] = numbers

# Ordina in modo cronologico reale (dal più recente al più vecchio)
lista_ordinate = sorted(
    estrazioni_dict.values(), 
    key=lambda x: datetime.strptime(x["data"], "%d/%m/%Y"), 
    reverse=True
)

if lista_ordinate:
    print(f"SUCCESSO: Estrazione piu recente inserita nel JSON: {lista_ordinate[0]['data']}")
else:
    print("ATTENZIONE: Nessuna estrazione valida elaborata.")

with open("estrazioni_complete.json", "w", encoding="utf-8") as f:
    json.dump(lista_ordinate, f, indent=2, ensure_ascii=False)

print("File estrazioni_complete.json generato correttamente.")
