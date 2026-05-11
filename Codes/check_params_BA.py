import json
from pathlib import Path

BASE = Path(__file__).parent
meta_path = BASE / "metadata_klima_v2_1h.json"

with open(meta_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 1) Alle verfügbaren Parameternamen anzeigen
print("Verfügbare Parameter im Dataset klima-v2-1h:\n")
names = []
for p in data.get("parameters", []):
    name = p.get("name")
    desc = p.get("description", "")
    unit = p.get("unit", "")
    names.append(name)
    print(f"- {name:15}  {desc}  [{unit}]")

# 2) Deine gewünschten Parameter dagegen checken
wanted = {
    "tl_mittel", "tlmax", "tlmin", "tsmin",
    "sh", "so_h", "rr", "vv_mittel",
    "ffx", "nebel", "glatt", "tau",
    "w_mittel"  # stand in der Fehlermeldung
}

available = set(names)

print("\nNicht im Stunden-Datensatz vorhandene Parameter:")
for w in sorted(wanted):
    if w not in available:
        print(" -", w)
