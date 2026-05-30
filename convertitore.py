import json
import os

mappa_ruote = {
    "BA": "BARI", "CA": "CAGLIARI", "FI": "FIRENZE", "GE": "GENOVA",
    "MI": "MILANO", "NA": "NAPOLI", "PA": "PALERMO", "RM": "ROMA",
    "TO": "TORINO", "VE": "VENEZIA", "RN": "NAZIONALE"
}

estrazioni_dict = {}

# Controlla se il file storico.txt esiste
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
            
        data = parti[0]  # Formato YYYY/MM/DD
        sigla_ruota = parti[1].upper()
        
        try:
            numeri = [int(parti[2]), int(parti[3]), int(parti[4]), int(parti[5]), int(parti[6])]
        except ValueError:
            continue
        
        nome_ruota = mappa_ruote.get(sigla_ruota)
        if not nome_ruota:
            continue
            
        if data not in estrazioni_dict:
            estrazioni_dict[data] = {
                "data": data,
                "concorso": "",
                "ruote": {}
            }
            
        estrazioni_dict[data]["ruote"][nome_ruota] = numeri

# Ordina dalla più recente alla più vecchia
lista_ordinate = sorted(estrazioni_dict.values(), key=lambda x: x["data"], reverse=True)

# Salva il file JSON finale
with open("estrazioni_complete.json", "w", encoding="utf-8") as f:
    json.dump(lista_ordinate, f, indent=2, ensure_ascii=False)

print("Conversione completata con successo in estrazioni_complete.json")
