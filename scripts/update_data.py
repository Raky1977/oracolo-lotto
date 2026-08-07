#!/usr/bin/env python3
"""Download the official Lotto historical ZIP and publish recent draws as JSON.

Designed for GitHub Actions and Lotto Italia Android app.
Source: https://www.brightstarlottery.it/STORICO_ESTRAZIONI_LOTTO/storico01-oggi.zip
Input TXT rows: YYYY/MM/DD<TAB>WHEEL_CODE<TAB>N1...N5
Output: estrazioni_recenti.json (newest first), compatible with Estrazione.kt.
"""
from __future__ import annotations

import io
import json
import os
import sys
import zipfile
from collections import defaultdict
from datetime import datetime, date
from pathlib import Path

import requests

SOURCE_URL = os.getenv(
    "LOTTO_ZIP_URL",
    "https://www.brightstarlottery.it/STORICO_ESTRAZIONI_LOTTO/storico01-oggi.zip",
)
OUT = Path(os.getenv("LOTTO_OUT", "estrazioni_recenti.json"))
KEEP = int(os.getenv("LOTTO_KEEP_DRAWS", "120"))

RUOTE = {
    "BA": "Bari",
    "CA": "Cagliari",
    "FI": "Firenze",
    "GE": "Genova",
    "MI": "Milano",
    "NA": "Napoli",
    "PA": "Palermo",
    "RM": "Roma",
    "RN": "Nazionale",
    "TO": "Torino",
    "VE": "Venezia",
}
EXPECTED = set(RUOTE.values())


def download_zip() -> bytes:
    local = os.getenv("LOTTO_LOCAL_ZIP")
    if local:
        return Path(local).read_bytes()
    r = requests.get(
        SOURCE_URL,
        timeout=45,
        headers={"User-Agent": "LottoItaliaDataUpdater/2.0 (+GitHub Actions)"},
    )
    r.raise_for_status()
    if not r.content.startswith(b"PK"):
        raise RuntimeError("La sorgente non ha restituito un file ZIP valido")
    return r.content


def read_txt(zip_bytes: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        txt_names = [n for n in zf.namelist() if n.lower().endswith(".txt")]
        if not txt_names:
            raise RuntimeError("Nessun file TXT trovato nello ZIP")
        # The official archive currently contains storico.txt. Take the largest TXT defensively.
        name = max(txt_names, key=lambda n: zf.getinfo(n).file_size)
        raw = zf.read(name)
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    raise RuntimeError("Impossibile decodificare lo storico TXT")


def parse(text: str) -> list[dict]:
    grouped: dict[str, dict[str, list[int]]] = defaultdict(dict)
    bad_rows = 0

    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 7:
            bad_rows += 1
            continue
        d, code, *nums_s = parts
        if code not in RUOTE:
            # Very old archives can contain only the wheels existing at that time.
            # Unknown codes are ignored rather than poisoning recent output.
            continue
        try:
            datetime.strptime(d, "%Y/%m/%d")
            nums = [int(x) for x in nums_s]
        except ValueError:
            bad_rows += 1
            continue
        if len(nums) != 5 or any(n < 1 or n > 90 for n in nums) or len(set(nums)) != 5:
            bad_rows += 1
            continue
        grouped[d][RUOTE[code]] = nums

    complete = []
    for d, wheels in grouped.items():
        # Only publish complete modern draws. This prevents a partially-updated ZIP
        # from replacing the last good extraction while the provider is uploading rows.
        if set(wheels) == EXPECTED:
            complete.append({
                "data": d,
                "concorso": "",  # Lotto Italia currently does not use this field.
                "ruote": {name: wheels[name] for name in RUOTE.values()},
            })

    complete.sort(key=lambda e: e["data"], reverse=True)
    if not complete:
        raise RuntimeError("Nessuna estrazione completa trovata")

    latest = datetime.strptime(complete[0]["data"], "%Y/%m/%d").date()
    if latest > date.today():
        raise RuntimeError(f"Data futura anomala nella sorgente: {latest}")

    if bad_rows:
        print(f"WARN: {bad_rows} righe non valide ignorate", file=sys.stderr)
    return complete[:KEEP]


def validate(draws: list[dict]) -> None:
    if not draws:
        raise RuntimeError("Output vuoto")
    dates = [x["data"] for x in draws]
    if len(dates) != len(set(dates)):
        raise RuntimeError("Date duplicate nell'output")
    for x in draws:
        if set(x["ruote"]) != EXPECTED:
            raise RuntimeError(f"Estrazione incompleta: {x['data']}")


def main() -> None:
    draws = parse(read_txt(download_zip()))
    validate(draws)

    # Atomic write: a failed run never destroys the last valid JSON.
    tmp = OUT.with_suffix(OUT.suffix + ".tmp")
    tmp.write_text(json.dumps(draws, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(OUT)

    print(f"OK latest={draws[0]['data']} draws={len(draws)} source={SOURCE_URL}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERRORE: {exc}", file=sys.stderr)
        sys.exit(1)
