import json
import os
from datetime import datetime

mappa_ruote = {
    "BA": "Bari", "CA": "Cagliari", "FI": "Firenze", "GE": "Genova",
    "MI": "Milano", "NA": "Napoli", "PA": "Palermo", "RM": "Roma",
    "TO": "Torino", "VE": "Venezia", "RN": "Nazionale"
}

estrazioni_dict = {}

print("--- AVVIO DIAGNOSTICA CONVERTITORE ---")

if not os.path.exists("storico.txt"):
    print("ERRORE CRUCIAL: storico.txt non trovato nel repository!")
    exit(1)

righe_totali = 0
righe_elaborate = 0
contatore_anni = {}

with open("storico.txt", "r", encoding="utf-8") as f:
    for riga in f:
        righe_totali += 1
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
            anno = data_oggetto.strftime("%Y")
            data_formattata = data_oggetto.strftime("%d/%m/%Y")
            
            # Conta quante righe elaboriamo per ogni anno per vedere dove si ferma
            contatore_anni[anno] = contatore_anni.get(anno, 0) + 1
        except Exception as e:
            # Se salta una riga per errore di formato lo scrive nei log di GitHub
            if righe_totali > 115000:  # Monitora solo le ultime righe (2024-2026)
                print(f"Errore parsing riga {righe_totali} ({data_grezza}): {str(e)}")
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
        righe_elaborate += 1

print(f"Righe totali lette nel txt: {righe_totali}")
print(f"Righe inserite correttamente nel dizionario: {righe_elaborate}")
print("Resoconto estrazioni per anno rilevate nel file di testo:")
for anno in sorted(contatore_anni.keys()):
    print(f" - Anno {anno}: {contatore_anni[anno]} righe ruota elaborate")

# Ordina in modo cronologico reale dal più recente al più vecchio
lista_ordinate = sorted(
    estrazioni_dict.values(), 
    key=lambda x: datetime.strptime(x["data"], "%d/%m/%Y"), 
    reverse=True
)

# Stampa di sicurezza per vedere qual è l'estrazione che Python mette in cima al JSON
if lista_ordinate:
    print(f"L'ESTRAZIONE PIÙ RECENTE GENERATA DA PYTHON È DEL: {lista_ordinate[0]['data']}")
else:
    print("ERRORE CRUCIAL: La lista finale è vuota!")

# Scrive il file JSON principale
with open("estrazioni_complete.json", "w", encoding="utf-8") as f:
    json.dump(lista_ordinate, f, indent=2, ensure_ascii=False)

# CREA UN FILE DI LOG TESTUALE DIRETTAMENTE SU GITHUB PER NOI
with open("log_diagnostica.txt", "w", encoding="utf-8") as f:
    f.write(f"Ultimo controllo eseguito il: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    f.write(f"Righe totali txt: {righe_totali}\n")
    if lista_ordinate:
        f.write(f"Data piu recente in cima al JSON: {lista_ordinate[0]['data']}\n")
        f.write(f"Data piu vecchia in fondo al JSON: {lista_ordinate[-1]['data']}\n")

print("File log_diagnostica.txt creato con successo.")
