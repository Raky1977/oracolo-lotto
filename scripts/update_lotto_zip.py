#!/usr/bin/env python3

from __future__ import annotations

import io
import json
import os
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, date
from pathlib import Path

import requests


SOURCE_URL = os.getenv(
    "LOTTO_ZIP_URL",
    "https://www.brightstarlottery.it/STORICO_ESTRAZIONI_LOTTO/storico01-oggi.zip",
)

OUT = Path(os.getenv("LOTTO_OUT", "estrazioni_recenti.json"))
ARTICLES_OUT = Path(os.getenv("LOTTO_ARTICLES_OUT", "articoli.json"))

KEEP = int(os.getenv("LOTTO_KEEP_DRAWS", "120"))
KEEP_ARTICLES = int(os.getenv("LOTTO_KEEP_ARTICLES", "50"))


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


# ==========================================================
# DOWNLOAD
# ==========================================================

def download_zip() -> bytes:
    local = os.getenv("LOTTO_LOCAL_ZIP")

    if local:
        return Path(local).read_bytes()

    r = requests.get(
        SOURCE_URL,
        timeout=45,
        headers={
            "User-Agent":
            "LottoItaliaDataUpdater/3.0 (+GitHub Actions)"
        },
    )

    r.raise_for_status()

    if not r.content.startswith(b"PK"):
        raise RuntimeError(
            "La sorgente non ha restituito un file ZIP valido"
        )

    return r.content


# ==========================================================
# LETTURA ZIP
# ==========================================================

def read_txt(zip_bytes: bytes) -> str:

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:

        txt_names = [
            n for n in zf.namelist()
            if n.lower().endswith(".txt")
        ]

        if not txt_names:
            raise RuntimeError(
                "Nessun file TXT trovato nello ZIP"
            )

        name = max(
            txt_names,
            key=lambda n: zf.getinfo(n).file_size
        )

        raw = zf.read(name)

    for enc in (
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin-1",
    ):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass

    raise RuntimeError(
        "Impossibile decodificare lo storico TXT"
    )


# ==========================================================
# PARSING
# ==========================================================

def parse(text: str) -> list[dict]:

    grouped: dict[
        str,
        dict[str, list[int]]
    ] = defaultdict(dict)

    bad_rows = 0

    for lineno, raw in enumerate(
        text.splitlines(), 1
    ):

        line = raw.strip()

        if not line:
            continue

        parts = line.split()

        if len(parts) != 7:
            bad_rows += 1
            continue

        d, code, *nums_s = parts

        if code not in RUOTE:
            continue

        try:

            datetime.strptime(
                d,
                "%Y/%m/%d"
            )

            nums = [
                int(x)
                for x in nums_s
            ]

        except ValueError:

            bad_rows += 1
            continue

        if (
            len(nums) != 5
            or any(
                n < 1 or n > 90
                for n in nums
            )
            or len(set(nums)) != 5
        ):

            bad_rows += 1
            continue

        grouped[d][
            RUOTE[code]
        ] = nums


    complete = []

    for d, wheels in grouped.items():

        if set(wheels) == EXPECTED:

            complete.append({
                "data": d,
                "concorso": "",
                "ruote": {
                    name: wheels[name]
                    for name
                    in RUOTE.values()
                },
            })


    complete.sort(
        key=lambda e: e["data"],
        reverse=True
    )

    if not complete:
        raise RuntimeError(
            "Nessuna estrazione completa trovata"
        )


    latest = datetime.strptime(
        complete[0]["data"],
        "%Y/%m/%d"
    ).date()

    if latest > date.today():

        raise RuntimeError(
            f"Data futura anomala "
            f"nella sorgente: {latest}"
        )


    if bad_rows:

        print(
            f"WARN: {bad_rows} "
            "righe non valide ignorate",
            file=sys.stderr,
        )


    return complete[:KEEP]


# ==========================================================
# VALIDAZIONE
# ==========================================================

def validate(draws: list[dict]) -> None:

    if not draws:
        raise RuntimeError(
            "Output vuoto"
        )

    dates = [
        x["data"]
        for x in draws
    ]

    if len(dates) != len(set(dates)):

        raise RuntimeError(
            "Date duplicate nell'output"
        )


    for x in draws:

        if set(x["ruote"]) != EXPECTED:

            raise RuntimeError(
                f"Estrazione incompleta: "
                f"{x['data']}"
            )


# ==========================================================
# UTILITY EDITORIALE
# ==========================================================

MONTHS = {
    1: "Gennaio",
    2: "Febbraio",
    3: "Marzo",
    4: "Aprile",
    5: "Maggio",
    6: "Giugno",
    7: "Luglio",
    8: "Agosto",
    9: "Settembre",
    10: "Ottobre",
    11: "Novembre",
    12: "Dicembre",
}


def pretty_date(value: str) -> str:

    d = datetime.strptime(
        value,
        "%Y/%m/%d"
    )

    return (
        f"{d.day} "
        f"{MONTHS[d.month]} "
        f"{d.year}"
    )


def load_articles() -> list[dict]:

    if not ARTICLES_OUT.exists():
        return []

    try:

        data = json.loads(
            ARTICLES_OUT.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(data, list):
            return data

    except Exception as exc:

        print(
            f"WARN articoli.json "
            f"non leggibile: {exc}",
            file=sys.stderr,
        )

    return []


# ==========================================================
# STATISTICHE
# ==========================================================

def wheel_frequencies(
    draws: list[dict],
    wheel: str,
    limit: int = 30,
) -> Counter:

    c = Counter()

    for draw in draws[:limit]:

        for n in draw["ruote"][wheel]:
            c[n] += 1

    return c


def wheel_delays(
    draws: list[dict],
    wheel: str,
) -> dict[int, int]:

    delays = {}

    for number in range(1, 91):

        delay = 0

        for draw in draws:

            if number in draw["ruote"][wheel]:
                break

            delay += 1

        delays[number] = delay

    return delays


def repeated_numbers(
    latest: dict,
    previous: dict,
) -> list[tuple[str, list[int]]]:

    result = []

    for wheel in RUOTE.values():

        repeated = sorted(
            set(latest["ruote"][wheel])
            &
            set(previous["ruote"][wheel])
        )

        if repeated:
            result.append(
                (wheel, repeated)
            )

    return result


# ==========================================================
# GENERAZIONE ARTICOLO
# ==========================================================

def generate_article(
    draws: list[dict],
    next_id: int,
) -> dict:

    latest = draws[0]

    previous = (
        draws[1]
        if len(draws) > 1
        else None
    )

    date_text = pretty_date(
        latest["data"]
    )


    # ------------------------------------------------------
    # RITARDATARIO PRINCIPALE
    # ------------------------------------------------------

    delay_records = []

    for wheel in RUOTE.values():

        delays = wheel_delays(
            draws,
            wheel
        )

        number, delay = max(
            delays.items(),
            key=lambda x: x[1]
        )

        delay_records.append(
            (delay, wheel, number)
        )


    delay_records.sort(
        reverse=True
    )

    max_delay, delay_wheel, delay_number = (
        delay_records[0]
    )


    # ------------------------------------------------------
    # FREQUENZA
    # ------------------------------------------------------

    freq_records = []

    for wheel in RUOTE.values():

        freq = wheel_frequencies(
            draws,
            wheel,
            30
        )

        if freq:

            number, count = freq.most_common(1)[0]

            freq_records.append(
                (
                    count,
                    wheel,
                    number
                )
            )


    freq_records.sort(
        reverse=True
    )

    freq_count, freq_wheel, freq_number = (
        freq_records[0]
    )


    # ------------------------------------------------------
    # PARI / DISPARI
    # ------------------------------------------------------

    all_latest = []

    for nums in latest["ruote"].values():
        all_latest.extend(nums)

    even = sum(
        1
        for n in all_latest
        if n % 2 == 0
    )

    odd = len(all_latest) - even


    # ------------------------------------------------------
    # RIPETIZIONI
    # ------------------------------------------------------

    repeats = (
        repeated_numbers(
            latest,
            previous
        )
        if previous
        else []
    )

    repeat_count = sum(
        len(nums)
        for _, nums in repeats
    )


    # ------------------------------------------------------
    # RUOTA FOCUS
    # ------------------------------------------------------

    focus_wheel = delay_wheel

    focus_nums = latest[
        "ruote"
    ][focus_wheel]

    focus_string = " - ".join(
        str(n)
        for n in focus_nums
    )


    # ------------------------------------------------------
    # TITOLI VARIABILI
    # ------------------------------------------------------

    title_variants = [

        (
            f"LOTTO {date_text.upper()}: "
            f"I NUMERI E LE CURIOSITÀ "
            f"DELL'ULTIMA ESTRAZIONE"
        ),

        (
            f"{date_text.upper()}: "
            f"COSA RACCONTA L'ULTIMA "
            f"ESTRAZIONE DEL LOTTO"
        ),

        (
            f"LOTTO {date_text.upper()}: "
            f"RITARDI, FREQUENZE "
            f"E NUMERI DA OSSERVARE"
        ),

        (
            f"DOPO L'ESTRAZIONE DEL "
            f"{date_text.upper()}: "
            f"LA NUOVA MAPPA STATISTICA"
        ),
    ]


    selector = (
        datetime.strptime(
            latest["data"],
            "%Y/%m/%d"
        ).toordinal()
        % len(title_variants)
    )

    title = title_variants[selector]


    # ------------------------------------------------------
    # ANTEPRIMA
    # ------------------------------------------------------

    preview = (
        f"L'estrazione del {date_text} "
        f"aggiorna frequenze e ritardi "
        f"delle undici ruote. "
        f"Focus su {delay_wheel}, "
        f"dove il {delay_number} "
        f"registra {max_delay} "
        f"concorsi di assenza."
    )


    # ------------------------------------------------------
    # RIPETIZIONI TESTO
    # ------------------------------------------------------

    if repeats:

        repeat_parts = []

        for wheel, nums in repeats[:4]:

            repeat_parts.append(
                f"**{wheel}**: "
                + ", ".join(
                    str(n)
                    for n in nums
                )
            )

        repeat_text = (
            "Rispetto al concorso precedente "
            f"si registrano **{repeat_count} "
            "ripetizioni sulla stessa ruota**. "
            "Tra quelle rilevate: "
            + "; ".join(repeat_parts)
            + "."
        )

    else:

        repeat_text = (
            "Confrontando il nuovo concorso "
            "con quello precedente non emergono "
            "ripetizioni sulla stessa ruota."
        )


    # ------------------------------------------------------
    # CONTENUTO
    # ------------------------------------------------------

    content = f"""# {title}

L'estrazione del **{date_text}** aggiorna il quadro statistico del Lotto italiano. Abbiamo confrontato il nuovo concorso con lo storico recente per individuare alcuni dati interessanti, senza attribuire alle statistiche capacità di prevedere le estrazioni future.

### 📍 La ruota sotto la lente: {focus_wheel}

I cinque numeri estratti su **{focus_wheel}** sono:

**{focus_string}**

Dopo questa estrazione, il **{delay_number}** risulta il numero con il ritardo più elevato tra quelli analizzati, con **{max_delay} concorsi consecutivi di assenza** sulla ruota di {delay_wheel}.

Il ritardo descrive esclusivamente ciò che è accaduto nelle estrazioni precedenti e non rende il numero più probabile nel concorso successivo.

### 🔥 Frequenze recenti

Analizzando le ultime **30 estrazioni** disponibili per ciascuna ruota, uno dei dati più evidenti riguarda **{freq_wheel}**: il numero **{freq_number}** è comparso **{freq_count} volte** nel periodo considerato.

Le frequenze recenti sono utili per descrivere il comportamento passato dei numeri, ma ogni nuova estrazione resta indipendente dalle precedenti.

### 🔁 Numeri che ritornano

{repeat_text}

### ⚖️ Pari e dispari

Considerando complessivamente i **55 numeri** estratti sulle undici ruote, il concorso presenta **{even} numeri pari** e **{odd} numeri dispari**.

È una fotografia semplice ma interessante della distribuzione dell'ultima estrazione.

### 📊 Il quadro dopo il concorso

La classifica dei maggiori ritardi viene ora guidata da **{delay_number} su {delay_wheel}**, mentre **{freq_number} su {freq_wheel}** emerge nell'analisi delle frequenze delle ultime 30 estrazioni.

L'archivio verrà nuovamente aggiornato con il prossimo concorso ufficiale.

⚠️ **Disclaimer:** il gioco del Lotto è basato esclusivamente sul caso. Ritardi, frequenze e statistiche descrivono estrazioni passate e non permettono di prevedere quelle future. Le informazioni riportate hanno finalità statistiche e informative. Gioca responsabilmente e solo se sei maggiorenne.
"""


    return {
        "id": next_id,
        "data": date_text,
        "titolo": title,
        "anteprima": preview,
        "contenuto": content,
        "draw_date": latest["data"],
        "automatico": True,
    }


# ==========================================================
# AGGIORNAMENTO EDITORIALE
# ==========================================================

def update_articles(
    draws: list[dict],
) -> bool:

    articles = load_articles()

    latest_date = draws[0]["data"]


    # Evita duplicati anche se GitHub Action
    # gira più volte nella stessa serata.
    for article in articles:

        if article.get(
            "draw_date"
        ) == latest_date:

            print(
                "Editoriale già presente "
                f"per {latest_date}"
            )

            return False


    # Compatibilità con eventuali articoli
    # automatici precedenti che non abbiano
    # draw_date.
    pretty = pretty_date(latest_date)

    for article in articles:

        if (
            article.get("automatico")
            and article.get("data") == pretty
        ):

            print(
                "Editoriale automatico "
                f"già presente per {pretty}"
            )

            return False


    max_id = max(
        (
            int(a.get("id", 0))
            for a in articles
        ),
        default=0,
    )


    article = generate_article(
        draws,
        max_id + 1
    )


    articles.insert(
        0,
        article
    )


    articles = articles[
        :KEEP_ARTICLES
    ]


    tmp = ARTICLES_OUT.with_suffix(
        ARTICLES_OUT.suffix + ".tmp"
    )

    tmp.write_text(
        json.dumps(
            articles,
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    tmp.replace(
        ARTICLES_OUT
    )


    print(
        "OK nuovo editoriale: "
        f"{article['titolo']}"
    )

    return True


# ==========================================================
# MAIN
# ==========================================================

def main() -> None:

    draws = parse(
        read_txt(
            download_zip()
        )
    )

    validate(draws)


    # Aggiornamento estrazioni
    tmp = OUT.with_suffix(
        OUT.suffix + ".tmp"
    )

    tmp.write_text(
        json.dumps(
            draws,
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    tmp.replace(OUT)


    # Editoriale automatico
    update_articles(draws)


    print(
        f"OK latest={draws[0]['data']} "
        f"draws={len(draws)} "
        f"source={SOURCE_URL}"
    )


if __name__ == "__main__":

    try:
        main()

    except Exception as exc:

        print(
            f"ERRORE: {exc}",
            file=sys.stderr,
        )

        sys.exit(1)
