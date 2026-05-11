import requests
import pandas as pd

# Deine 24 Stationen
STATION_IDS = [4,7,8,15,17,24,26,30,39,48,55,56,65,71,80,85,89,105,106,107,122,142,204,213]

# Metadata URL direkt von GeoSphere
META_URL = "https://dataset.api.hub.geosphere.at/v1/station/historical/klima-v2-1h/metadata"

print("Lade Metadata von GeoSphere ...")
r = requests.get(META_URL, timeout=60)
r.raise_for_status()
meta = r.json()

stations = meta.get("stations", [])

rows = []

for st in stations:
    sid = st.get("id")
    if sid in STATION_IDS:
        lat = st.get("lat", st.get("latitude"))
        lon = st.get("lon", st.get("longitude"))

        rows.append({
            "station_id": sid,
            "station_name": st.get("name", ""),
            "bundesland": st.get("state", ""),
            "latitude": lat,
            "longitude": lon
        })

df = pd.DataFrame(rows).sort_values(["bundesland","station_name"])

# Speichert automatisch auf Desktop
out_path = r"C:\Users\omarm\Desktop\geosphere_stations_points.csv"
df.to_csv(out_path, index=False, encoding="utf-8")

print(" Fertig!")
print("Datei gespeichert unter:")
print(out_path)
print("\nStationen gefunden:", len(df))