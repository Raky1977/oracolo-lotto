import json
import os
from datetime import datetime

# Mappa corretta per la logica dell'applicazione (Iniziale Maiuscola)
mappa_ruote = {
    "BA": "Bari", "CA": "Cagliari", "FI": "Firenze", "GE": "Genova",
    "MI": "Milano", "NA": "Napoli", "PA": "Palermo", "RM": "Roma",
    "TO": "Torino", "VE": "Venezia", "RN": "Nazionale"
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

# Ordina in modo cronologico (dal più recente al più vecchio)
lista_ordinate = sorted(
    estrazioni_dict.values(), 
    key=lambda x: datetime.strptime(x["data"], "%d/%m/%Y"), 
    reverse=True
)

with open("estrazioni_complete.json", "w", encoding="utf-8") as f:
    json.dump(lista_ordinate, f, indent=2, ensure_ascii=False)

print("Conversione completata con ruote formattate per l'applicazione!")
