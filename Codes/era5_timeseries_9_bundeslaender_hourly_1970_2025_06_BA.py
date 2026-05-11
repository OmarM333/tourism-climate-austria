import cdsapi

# 9 Bundesländer – repräsentative Koordinaten (Zentrum / Landeshauptstadt-Nähe)
POINTS = {
    "wien": (48.21, 16.37),                #Wien
    "niederoesterreich": (48.20, 15.63),   # St. Pölten
    "oberoesterreich": (48.31, 14.29),     # Linz
    "steiermark": (47.07, 15.44),          # Graz
    "kaernten": (46.62, 14.31),            # Klagenfurt
    "salzburg": (47.81, 13.04),            # Salzburg
    "tirol": (47.27, 11.39),               # Innsbruck
    "vorarlberg": (47.24, 9.60),           # Feldkirch
    "burgenland": (47.85, 16.52),          # Eisenstadt
}

START = "1970-01-01"
END   = "2025-06-30"

# Nimm erstmal nur 2m_temperature, damit es sicher durchläuft.
# Danach kannst du mehr Variablen hinzufügen (siehe unten).
VARIABLES = [
    "2m_temperature",
    # "2m_dewpoint_temperature",
    # "total_precipitation",
    # "10m_u_component_of_wind",
    # "10m_v_component_of_wind",
    # "surface_pressure",
]

c = cdsapi.Client()

for bl, (lat, lon) in POINTS.items():
    outfile = f"era5_timeseries_{bl}_{START}_{END}_hourly.csv"
    print(f"Downloading {bl} -> {outfile}")

    c.retrieve(
        "reanalysis-era5-single-levels-timeseries",
        {
            "variable": VARIABLES,
            "location": {"latitude": lat, "longitude": lon},
            "date": [f"{START}/{END}"],
            "data_format": "csv",      # CSV ist am einfachsten in KNIME
        },
        outfile
    )

print("DONE.")

