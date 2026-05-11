#!/bin/bash

STATIONS="65,122,71,48,80,89,4,204,26,56,213,85,7,30,17,8,39,55,142,24,15,105,106,107"
PARAMS="tl_mittel,tlmax,tlmin,tsmin,sh,rr,so_h"

YEARS=(
  "1973-01-01:1979-12-31"
  "1980-01-01:1989-12-31"
  "1990-01-01:1999-12-31"
  "2000-01-01:2009-12-31"
  "2010-01-01:2019-12-31"
  "2020-01-01:2025-12-31"
)

for PERIOD in "${YEARS[@]}"; do # schleife
    START=${PERIOD%%:*}
    END=${PERIOD##*:}
    FILE="daily_${START}_${END}.csv"  #Dateiname erzeugen

    echo "⬇ Lade Tagesdaten $START bis $END → $FILE"

    curl -s \
      "https://dataset.api.hub.geosphere.at/v1/station/historical/klima-v2-1d?start=$START&end=$END&station_ids=$STATIONS&parameters=$PARAMS&format=csv" \
      -o "$FILE"   #API Call

    echo "$FILE fertig"
    sleep 5
done

echo " Alle Tages-Downloads abgeschlossen!"

