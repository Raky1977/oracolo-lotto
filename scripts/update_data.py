import requests
import json
from datetime import datetime

url = "https://www.lottomatica.it/lotto/risultati"

headers = {
 "User-Agent": "Mozilla/5.0"
}

print("Script partito")

try:

 r = requests.get(url,headers=headers,timeout=10)

 if r.status_code != 200:
  print("Errore sito:",r.status_code)
  exit()

 html = r.text

 # esempio semplice di parsing numeri
 import re

 numeri = re.findall(r'\b\d{1,2}\b',html)

 if len(numeri) < 55:
  print("Non trovo abbastanza numeri")
  exit()

 ruote = {
  "Bari":list(map(int,numeri[0:5])),
  "Cagliari":list(map(int,numeri[5:10])),
  "Firenze":list(map(int,numeri[10:15])),
  "Genova":list(map(int,numeri[15:20])),
  "Milano":list(map(int,numeri[20:25])),
  "Napoli":list(map(int,numeri[25:30])),
  "Palermo":list(map(int,numeri[30:35])),
  "Roma":list(map(int,numeri[35:40])),
  "Torino":list(map(int,numeri[40:45])),
  "Venezia":list(map(int,numeri[45:50])),
  "Nazionale":list(map(int,numeri[50:55]))
 }

 risultato = {
  "lotto":[
   {
    "data":datetime.now().strftime("%d/%m/%Y"),
    "ruote":ruote
   }
  ],
  "last_global_update":datetime.now().strftime("%d/%m/%Y %H:%M")
 }

 with open("estrazioni.json","w") as f:
  json.dump(risultato,f,indent=4)

 print("JSON aggiornato")

except Exception as e:
 print("Errore:",e)
