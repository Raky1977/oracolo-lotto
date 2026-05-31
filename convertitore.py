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

print("--- AVVIO CONVERTITORE ---")

if not os.path.exists("storico.txt"):
    print("Errore: storico.txt non trovato!")
    exit(1)

with open("storico.txt", "r", encoding="utf-8") as f:
    for num_riga, riga in enumerate(f, 1):
        riga = riga.strip()
        if not riga:
            continue
            
        parti = re.split(r'\t+|\s+', riga)
        if len(parti) < 7:
            continue
            
        data_grezza = parti[0].strip().replace("-", "/")
        sigla_ruota = parti[1].strip().upper()
        
        try:
            numeri_estrazione = [
                int(parti[2]), 
                int(parti[3]), 
                int(parti[4]), 
                int(parti[5]), 
                int(parti[6])
            ]
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
            
        estrazioni_dict[data_formattata]["ruote"][nome_ruota] = numeri_estrazione

# Ordinamento cronologico decrescente (le più recenti in cima)
lista_ordinate = sorted(
    estrazioni_dict.values(), 
    key=lambda x: datetime.strptime(x["data"], "%d/%m/%Y"), 
    reverse=True
)

# 1. Salvataggio del database completo (per installazioni pulite o ripristini)
with open("estrazioni_complete.json", "w", encoding="utf-8") as f:
    json.dump(lista_ordinate, f, indent=2, ensure_ascii=False)

# 2. Salvataggio del file incrementale leggero (ultime 15 estrazioni per l'aggiornamento dell'app)
lista_recenti = lista_ordinate[:15]
with open("estrazioni_recenti.json", "w", encoding="utf-8") as f:
    json.dump(lista_recenti, f, indent=2, ensure_ascii=False)

# 3. Scrittura dei log di diagnostica
with open("log_diagnostica.txt", "w", encoding="utf-8") as f:
    f.write(f"Ultimo controllo eseguito il: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    if lista_ordinate:
        f.write(f"Data piu recente in cima al JSON completo: {lista_ordinate[0]['data']}\n")
    if lista_recenti:
        f.write(f"Data piu vecchia nel JSON incrementale: {lista_recenti[-1]['data']}\n")

print("Conversione completata con successo!")
