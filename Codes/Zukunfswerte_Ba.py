import pandas as pd
from pathlib import Path

# === 1) Pfad zu deinen 4 CSVs anpassen ===
base = Path(r"C:\Users\omarm\OneDrive\Desktop\FH\BIG DATA\Dataset\Zukunftsszenario-wetter")  # 

files = {
    "tasmin": base / "tasmin_Amon_EC-Earth3_ssp434_r101i1p1f1_gr_20160116-20491216.csv",
    "tasmax": base / "tasmax_Amon_EC-Earth3_ssp434_r101i1p1f1_gr_20160116-20491216.csv",
    "ta":     base / "ta_Amon_EC-Earth3_ssp434_r101i1p1f1_gr_20160116-20491216.csv",
    "pr":     base / "pr_Amon_EC-Earth3_ssp434_r101i1p1f1_gr_20160116-20491216.csv",
}

# === 2) 9 Bundesländer: repräsentative Punkte  ===
POINTS = {
    "Wien": (48.2082, 16.3738),
    "Niederoesterreich": (48.2, 15.6),
    "Oberoesterreich": (48.3, 14.3),
    "Steiermark": (47.2, 15.6),
    "Kaernten": (46.6, 14.3),
    "Salzburg": (47.8, 13.0),
    "Tirol": (47.3, 11.4),
    "Vorarlberg": (47.2, 9.9),
    "Burgenland": (47.8, 16.6),
}

def nearest_point(df, lat0, lon0):
    pts = df[["lat","lon"]].drop_duplicates().copy()
    pts["d2"] = (pts["lat"] - lat0)**2 + (pts["lon"] - lon0)**2
    best = pts.loc[pts["d2"].idxmin(), ["lat","lon"]]
    return df[(df["lat"] == best["lat"]) & (df["lon"] == best["lon"])].copy()

def load_var(var, path):
    df = pd.read_csv(path)
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    # behalte nur das Notwendige
    keep = ["time", "lat", "lon", var]
    df = df[[c for c in keep if c in df.columns]]
    return df

# === 3) Pro Variable -> pro Bundesland 1 Zeitreihe extrahieren ===
per_var = {}
for var, path in files.items():
    df = load_var(var, path)
    out = []
    for bl, (lat0, lon0) in POINTS.items():
        sub = nearest_point(df, lat0, lon0)
        sub = sub[["time", var]].copy()
        sub["bundesland"] = bl
        out.append(sub)
    per_var[var] = pd.concat(out, ignore_index=True)

# === 4) Merge auf (bundesland, time) ===
merged = per_var["tasmin"]
for v in ["tasmax", "ta", "pr"]:
    merged = merged.merge(per_var[v], on=["bundesland", "time"], how="inner")

# === 5) Filter 2025–2050 (du kannst 2049/2050 je nach Datei anpassen) ===
merged = merged[(merged["time"] >= "2025-01-01") & (merged["time"] <= "2050-12-31")].copy()

# === 6) Kelvin -> °C (tasmin, tasmax, ta) ===
merged["tasmin_c"] = merged["tasmin"] - 273.15
merged["tasmax_c"] = merged["tasmax"] - 273.15
merged["ta_c"]     = merged["ta"]     - 273.15

# Optional: Original-Kelvin-Spalten weg
merged = merged.drop(columns=["tasmin", "tasmax", "ta"])

# === 7) Sortieren & speichern ===
merged = merged.sort_values(["bundesland", "time"])

out_path = base / "cmip6_ssp434_ec-earth3_AT_9BL_monthly_2025_2050.csv"
merged.to_csv(out_path, index=False)

print("DONE:", out_path)
print("Columns:", list(merged.columns))
