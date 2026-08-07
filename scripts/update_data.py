import json, re, sys
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup

ADM_URL = "https://www.adm.gov.it/portale/monopoli/giochi/gioco-del-lotto/lotto_g"
OUT = Path("estrazioni_recenti.json")
RUOTE = ["Bari","Cagliari","Firenze","Genova","Milano","Napoli","Palermo","Roma","Torino","Venezia","Nazionale"]


def fetch_latest():
    r = requests.get(ADM_URL, timeout=30, headers={"User-Agent":"Mozilla/5.0 LottoItaliaDataUpdater/1.0"})
    r.raise_for_status()
    text = BeautifulSoup(r.text, "html.parser").get_text(" ", strip=True)

    m = re.search(r"Estrazione\s+n[°º]?\s*(\d+)\s+del\s+(\d{2}/\d{2}/\d{4})", text, re.I)
    if not m:
        raise RuntimeError("Numero/data estrazione ADM non riconosciuti")
    concorso, data_it = m.group(1), m.group(2)

    ruote = {}
    for i, ruota in enumerate(RUOTE):
        start = text.upper().find(ruota.upper())
        if start < 0:
            raise RuntimeError(f"Ruota {ruota} non trovata")
        end_candidates = [text.upper().find(r.upper(), start + len(ruota)) for r in RUOTE[i+1:]]
        end_candidates = [x for x in end_candidates if x > start]
        end = min(end_candidates) if end_candidates else text.upper().find("SIMBOLOTTO", start)
        if end < 0: end = start + 500
        chunk = text[start + len(ruota):end]
        nums = [int(x) for x in re.findall(r"\b(?:[1-9]|[1-8]\d|90)\b", chunk)]
        if len(nums) < 5:
            raise RuntimeError(f"Numeri insufficienti per {ruota}: {nums}")
        ruote[ruota] = nums[:5]

    dt = datetime.strptime(data_it, "%d/%m/%Y")
    return {"data": dt.strftime("%Y/%m/%d"), "concorso": concorso, "ruote": ruote}


def main():
    latest = fetch_latest()
    old = []
    if OUT.exists():
        try: old = json.loads(OUT.read_text(encoding="utf-8"))
        except Exception: old = []
    if not isinstance(old, list): old = []

    key = lambda e: (e.get("data"), str(e.get("concorso", "")))
    merged = [latest] + [e for e in old if key(e) != key(latest)]
    merged = sorted(merged, key=lambda e: e.get("data", ""), reverse=True)[:80]
    OUT.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {latest['data']} concorso {latest['concorso']}")

if __name__ == "__main__":
    try: main()
    except Exception as exc:
        print(f"ERRORE: {exc}", file=sys.stderr)
        sys.exit(1)
