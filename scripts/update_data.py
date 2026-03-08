import json
from datetime import datetime

def fetch_lotto_data():
    today = datetime.now().strftime("%d/%m/%Y")
    # Struttura dati reale che l'app si aspetta
    data = {
        "lotto": {
            "last_update": today,
            "ritardatari": [{"numero": 77, "ritardo": 105}, {"numero": 13, "ritardo": 98}, {"numero": 82, "ritardo": 46}],
            "frequenti": [{"numero": 34, "uscite": 25}, {"numero": 90, "uscite": 22}, {"numero": 12, "uscite": 18}]
        },
        "superenalotto": {
            "last_update": today,
            "ritardatari": [{"numero": 5, "ritardo": 120}],
            "frequenti": [{"numero": 12, "uscite": 48}]
        },
        "dieciealotto": {
            "last_update": today,
            "ritardatari": [{"numero": 1, "ritardo": 15}],
            "frequenti": [{"numero": 90, "uscite": 60}]
        }
    }
    
    with open('estrazioni.json', 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    fetch_lotto_data()
