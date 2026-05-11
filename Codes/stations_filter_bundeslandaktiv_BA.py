from pathlib import Path
import json
from collections import defaultdict

# Zeitraum, den die Station abdecken soll
START_BOUND = "1973-01-01T00:00:00+00:00"
END_BOUND   = "2025-10-01T00:00:00+00:00"

BASE = Path(__file__).parent

# 1) Metadaten des Stunden-Datensatzes klima-v2-1h laden
meta_path = BASE / "metadata_klima_v2_1h.json"
with open(meta_path, "r", encoding="utf-8") as f:
    data_hourly = json.load(f)

# Sicherheitscheck, falls wieder irgendwas Falsches geladen wurde
if "stations" not in data_hourly:
    print(" In metadata_klima_v2_1h.json gibt es keinen Key 'stations'.")
    print("   Bist du sicher, dass du die Datei mit der URL")
    print("   https://dataset.api.hub.geosphere.at/v1/station/historical/klima-v2-1h/metadata")
    print("   heruntergeladen hast?")
    print("   Top-Level-Keys sind:", list(data_hourly.keys()))
    raise SystemExit(1)

stations_all = data_hourly["stations"]

# 2) Filtern: Station muss den gesamten Zeitraum 1973–2025 abdecken
filtered = []
for st in stations_all:
    valid_from = st.get("valid_from") or ""
    valid_to = st.get("valid_to") or ""

    if valid_from <= START_BOUND and valid_to >= END_BOUND:
        filtered.append(st)

# 3) Pro Bundesland sammeln (Feldname 'state' wie in deinem alten Code)
by_state = defaultdict(list)
for st in filtered:
    state = st.get("state", "UNKNOWN")
    by_state[state].append(st)

# 4) Pro Bundesland max. 3 Stationen auswählen
selected = []
for state, sts in sorted(by_state.items(), key=lambda x: x[0]):  # nach Bundesland sortieren
    sts.sort(key=lambda x: x.get("valid_from", ""))  # älteste zuerst
    selected.extend(sts[:3])

# 5) Übersicht ausgeben
print("Bundesland;ID;Name;Von;Bis")
for st in selected:
    print(
        f'{st.get("state","")};'
        f'{st["id"]};'
        f'{st.get("name","")};'
        f'{st.get("valid_from","")};'
        f'{st.get("valid_to","")}'
    )

# 6) IDs für dein Bash-Script
ids = ",".join(str(st["id"]) for st in selected)
print("\nSTATIONS=\"{}\"".format(ids))

