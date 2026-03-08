import json
from datetime import datetime

def update_estrazioni():
    # Database delle estrazioni dal 01/01/2026
    # Nota: Questi dati sono la base che l'app userà per i calcoli
    database = {
        "lotto": [
            {"data": "07/03/2026", "numeri": [10, 22, 45, 77, 3]},
            {"data": "05/03/2026", "numeri": [1, 15, 33, 44, 12]},
            {"data": "03/03/2026", "numeri": [88, 12, 43, 5, 21]},
            {"data": "28/02/2026", "numeri": [10, 55, 67, 34, 2]},
            {"data": "26/02/2026", "numeri": [90, 45, 23, 11, 8]},
            {"data": "24/02/2026", "numeri": [14, 56, 78, 32, 9]},
            {"data": "21/02/2026", "numeri": [2, 19, 40, 61, 88]},
            # Aggiungeremo qui le altre man mano o tramite scraping
        ],
        "superenalotto": [
            {"data": "07/03/2026", "numeri": [5, 18, 23, 45, 67, 89]},
            {"data": "05/03/2026", "numeri": [2, 12, 34, 56, 71, 80]}
        ],
        "last_global_update": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    
    with open('estrazioni.json', 'w') as f:
        json.dump(database, f, indent=4)

if __name__ == "__main__":
    update_estrazioni()
