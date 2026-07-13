#!/usr/bin/env bash
set -euo pipefail

WORK=/workspace/goal4875_section57_au_representative/author_repeat
AUTHOR=/workspace/RayJoin_goal4867_author_dump/release/bin/polyover_exec
LEFT=/workspace/goal4848_rep/current_osm_au/lakes_Australia_current_osm_Point.cdb
RIGHT=/workspace/goal4848_rep/current_osm_au/parks_Australia_current_osm_Point.cdb
SER=/workspace/goal4875_section57_au_representative/serialize_author_au

mkdir -p "$WORK"
for i in 1 2 3; do
  OUT="$WORK/out_${i}.txt"
  LOG="$WORK/out_${i}.log"
  "$AUTHOR" \
    -poly1 "$LEFT" \
    -poly2 "$RIGHT" \
    -serialize="$SER" \
    -grid_size=15000 \
    -mode=rt \
    -v=1 \
    -fau \
    -xsect_factor 0.1 \
    -enlarge=3.5 \
    -check=false \
    -output "$OUT" \
    >"$LOG" 2>&1
  echo "RUN=$i"
  sha256sum "$OUT"
  wc -l -c "$OUT"
  grep -E 'Map [01], Xsect|Total chains|Timing results' "$LOG" | tail -10 || true
done
