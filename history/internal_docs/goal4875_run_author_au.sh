#!/usr/bin/env bash
set -euo pipefail

WORK=/workspace/goal4875_section57_au_representative
AUTHOR=/workspace/RayJoin_goal4867_author_dump/release/bin/polyover_exec
LEFT=/workspace/goal4848_rep/current_osm_au/lakes_Australia_current_osm_Point.cdb
RIGHT=/workspace/goal4848_rep/current_osm_au/parks_Australia_current_osm_Point.cdb
SER="$WORK/serialize_author_au"
OUT="$WORK/author_patch_au_overlay.txt"
LOG="$WORK/author_patch_au_overlay.log"

mkdir -p "$WORK"
rm -f "$OUT" "$LOG"

start_ns=$(python3 - <<'PY'
import time
print(time.time_ns())
PY
)

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

end_ns=$(python3 - <<'PY'
import time
print(time.time_ns())
PY
)
echo "AUTHOR_WALL_SEC=$(( (end_ns - start_ns) / 1000000000 ))" >> "$LOG"

python3 - <<'PY'
from pathlib import Path
import hashlib
import json

out = Path("/workspace/goal4875_section57_au_representative/author_patch_au_overlay.txt")
log = Path("/workspace/goal4875_section57_au_representative/author_patch_au_overlay.log")
h = hashlib.sha256()
lines = 0
if out.exists():
    with out.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            lines += chunk.count(b"\n")
            h.update(chunk)
summary = {
    "schema": "rtdl.goal4875.authorpatch.au_representative.summary.v1",
    "exists": out.exists(),
    "bytes": out.stat().st_size if out.exists() else None,
    "lines": lines,
    "sha256": h.hexdigest() if out.exists() else None,
    "log_tail": log.read_text(errors="replace")[-4000:] if log.exists() else "",
}
Path("/workspace/goal4875_section57_au_representative/author_patch_au_overlay_summary.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True),
    encoding="utf-8",
)
print(json.dumps(summary, indent=2, sort_keys=True))
PY
