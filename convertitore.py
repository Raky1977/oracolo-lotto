import json
import os
from datetime import datetime

mappa_ruote = {
    "BA": "BARI", "CA": "CAGLIARI", "FI": "FIRENZE", "GE": "GENOVA",
    "MI": "MILANO", "NA": "NAPOLI", "PA": "PALERMO", "RM": "ROMA",
    "TO": "TORINO", "VE": "VENEZIA", "RN": "NAZIONALE"
}

estrazioni_dict = {}

if not os.path.exists("storico.txt"):
    print("Errore: storico.txt non trovato!")
    exit(1)

with open("storico.txt", "r", encoding="utf-8") as f:
    for riga in f:
        riga = riga.strip()
        if not riga:
            continue
        
        parti = riga.split("\t")
        if len(parti) < 7:
            continue
            
        data_grezza = parti[0]  # Formato YYYY/MM/DD
        sigla_ruota = parti[1].upper()
        
        try:
            numeri = [int(parti[2]), int(parti[3]), int(parti[4]), int(parti[5]), int(parti[6])]
            data_oggetto = datetime.strptime(data_grezza, "%Y/%m/%d")
            data_formattata = data_oggetto.strftime("%d/%m/%Y")
        except Exception:
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
            
        estrazioni_dict[data_formattata]["ruote"][nome_ruota] = numeri

# Ordina le estrazioni in modo cronologico reale (dalla più recente alla più vecchia)
lista_ordinate = sorted(
    estrazioni_dict.values(), 
    key=lambda x: datetime.strptime(x["data"], "%d/%m/%Y"), 
    reverse=True
)

with open("estrazioni_complete.json", "w", encoding="utf-8") as f:
    json.dump(lista_ordinate, f, indent=2, ensure_ascii=False)

print("Conversione e ordinamento cronologico completati!")
