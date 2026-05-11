import requests
import pandas as pd

STATIONS = [int(x) for x in "65,122,71,48,80,89,4,204,26,56,213,85,7,30,17,8,39,55,142,24,15,105,106,107".split(",")]
PARAMS   = ["tl", "tsmin", "sh", "rr", "so_h"]  # wichtig für deine Forschungsfrage

BASE_URL = "https://dataset.api.hub.geosphere.at/v1/station/historical/klima-v2-1h"

YEARS = [1973, 1980, 1990, 2000, 2010, 2022]
WINDOWS = [("01-01", "01-07"), ("02-01", "02-07")]  # 2 Wochen-Samples pro Jahr

MISSING_SENTINELS = {"", "NA", "NaN", "nan", None}

def is_missing(x):
    if x in MISSING_SENTINELS:
        return True
    # häufige Missing-Codes in Klima-Daten
    try:
        xf = float(x)
        if xf in (-999, -999.0, -9999, -9999.0):
            return True
    except Exception:
        pass
    return False

def find_param_series(obj, param, n):
    """
    Sucht irgendwo in der JSON-Struktur nach einer Liste mit Länge n,
    die zu 'param' passt. Robust gegen unterschiedliche Strukturen.
    """
    target_keys = {param, param.lower(), param.upper()}

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                # direkter Treffer: key == param und value ist Liste
                if isinstance(k, str) and k in target_keys:
                    if isinstance(v, list) and len(v) == n:
                        return v
                    # manchmal steckt es als {"data":[...]}
                    if isinstance(v, dict):
                        dv = v.get("data") or v.get("values")
                        if isinstance(dv, list) and len(dv) == n:
                            return dv
                # weiter suchen
                got = walk(v)
                if got is not None:
                    return got
        elif isinstance(o, list):
            for it in o:
                got = walk(it)
                if got is not None:
                    return got
        return None

    return walk(obj)

def find_station_id(feature):
    # station_id kann in properties oder direkt vorkommen
    for path in [
        ("properties", "station_id"),
        ("properties", "id"),
        ("station_id",),
        ("id",),
    ]:
        cur = feature
        ok = True
        for p in path:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                ok = False
                break
        if ok:
            try:
                return int(cur)
            except Exception:
                pass
    return None

def fetch_json(station_id, start, end, params):
    url = (
        f"{BASE_URL}"
        f"?start={start}&end={end}"
        f"&station_ids={station_id}"
        f"&parameters={','.join(params)}"
    )
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    return r.json()

rows = []

for sid in STATIONS:
    print(f"\n=== Station {sid} ===")
    for y in YEARS:
        for (m1, m2) in WINDOWS:
            start = f"{y}-{m1}"
            end   = f"{y}-{m2}"
            print(f"  Prüfe {start} bis {end} ...", end=" ")

            try:
                js = fetch_json(sid, start, end, PARAMS)

                timestamps = js.get("timestamps", [])
                n = len(timestamps)
                if n == 0:
                    raise RuntimeError("Keine timestamps in Antwort")

                # FeatureCollection enthält meist features; wir nehmen die erste Feature (bei station_ids=1)
                features = js.get("features", [])
                if not features:
                    raise RuntimeError("Keine features in Antwort")

                feat = features[0]
                sid_found = find_station_id(feat) or sid

                for p in PARAMS:
                    series = find_param_series(feat, p, n)
                    if series is None:
                        rows.append({"station_id": sid_found, "year": y, "window": f"{m1}-{m2}",
                                     "parameter": p, "rows": n, "non_missing": 0, "coverage_pct": 0.0})
                        continue

                    nonmiss = sum(0 if is_missing(v) else 1 for v in series)
                    rows.append({"station_id": sid_found, "year": y, "window": f"{m1}-{m2}",
                                 "parameter": p, "rows": n, "non_missing": nonmiss,
                                 "coverage_pct": round(nonmiss / n * 100, 2)})

                print("OK")
            except Exception as e:
                print("FAIL")
                rows.append({"station_id": sid, "year": y, "window": f"{m1}-{m2}",
                             "parameter": "ALL", "rows": 0, "non_missing": 0, "coverage_pct": 0.0,
                             "error": str(e)[:220]})

rep = pd.DataFrame(rows)

# Pivot: mittlere Coverage über alle Samples (Jahre/Fenster)
good = rep[rep["parameter"].isin(PARAMS)].copy()
pivot = (good.groupby(["station_id", "parameter"])["coverage_pct"]
         .mean()
         .reset_index()
         .pivot(index="station_id", columns="parameter", values="coverage_pct")
         .sort_index())

out_dir = r"C:\Users\omarm\Desktop\FH\BIG DATA\Dataset\Zang"
rep.to_csv(out_dir + r"\http_probe_json_raw.csv", index=False, encoding="utf-8")
pivot.to_csv(out_dir + r"\http_probe_json_mean_coverage.csv", encoding="utf-8")

print("\n Fertig:")
print(" -", out_dir + r"\http_probe_json_raw.csv")
print(" -", out_dir + r"\http_probe_json_mean_coverage.csv")

if "sh" in pivot.columns:
    print("\nTop 10 Stationen nach 'sh' (Probe-Coverage):")
    print(pivot["sh"].sort_values(ascending=False).head(10))

