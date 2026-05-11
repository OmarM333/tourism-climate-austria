#!/bin/bash

STATIONS="65,122,71,48,80,89,4,204,26,56,213,85,7,30,17,8,39,55,142,24,15,105,106,107"
PARAMS="tl,tsmin,sh,so_h,rr,rrm,ff,ffx,dd,rf,p,cglo"

START_GLOBAL="2025-08-01"

END_GLOBAL="2025-12-30"   
STEP_DAYS=120

START="$START_GLOBAL"

while [[ "$START" < "$END_GLOBAL" ]]; do
    NEXT=$(date -I -d "$START +${STEP_DAYS} days")
    if [[ "$NEXT" > "$END_GLOBAL" ]]; then
        NEXT="$END_GLOBAL"
    fi
    END_REQ=$(date -I -d "$NEXT -1 day")

    FILE="stunden_alle_${START}_${END_REQ}.csv"

    # Wenn Datei schon da ist → überspringen
    if [[ -f "$FILE" ]]; then
        echo "  Überspringe vorhandene Datei $FILE"
        START="$NEXT"
        continue
    fi

    echo "⬇ Lade $START bis $END_REQ → $FILE"

    curl -s \
      "https://dataset.api.hub.geosphere.at/v1/station/historical/klima-v2-1h?start=${START}&end=${END_REQ}&station_ids=${STATIONS}&parameters=${PARAMS}&format=csv" \
      -o "$FILE"

    echo " Fertig: $FILE"
    sleep 3

    START="$NEXT"
done

echo " Alle Stunden-Downloads abgeschlossen!"
