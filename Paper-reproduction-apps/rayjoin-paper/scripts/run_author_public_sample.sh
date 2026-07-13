#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${RAYJOIN_DATA_DIR:-${APP_DIR}/_data/public_sample}"
OUT_DIR="${RAYJOIN_OUT_DIR:-${APP_DIR}/_runs/public_sample/author_official}"
BUILD_DIR="${RAYJOIN_AUTHOR_BUILD_DIR:-${APP_DIR}/_work/author_official/release}"

QUERY_EXEC="${BUILD_DIR}/bin/query_exec"
POLYOVER_EXEC="${BUILD_DIR}/bin/polyover_exec"
COUNTY="${DATA_DIR}/br_county_clean_25_odyssey_final.txt"
SOIL="${DATA_DIR}/br_soil_ascii_odyssey_final.txt"
ANSWER="${DATA_DIR}/br_countyXbr_soil_answer.txt"

mkdir -p "${OUT_DIR}" "${OUT_DIR}/serialize"

if [ ! -x "${QUERY_EXEC}" ] || [ ! -x "${POLYOVER_EXEC}" ]; then
  echo "AuthorOfficial binaries not found. Run scripts/setup_author_official.sh first." >&2
  exit 2
fi

"${QUERY_EXEC}" \
  -poly1 "${COUNTY}" \
  -poly2 "${SOIL}" \
  -mode=rt \
  -query=lsi \
  -xsect_factor=0.1 \
  -check=false \
  -warmup=0 \
  -repeat=1 \
  >"${OUT_DIR}/section52_lsi.stdout.txt" \
  2>"${OUT_DIR}/section52_lsi.stderr.txt"

"${QUERY_EXEC}" \
  -poly1 "${COUNTY}" \
  -poly2 "${SOIL}" \
  -mode=rt \
  -query=pip \
  -xsect_factor=0.1 \
  -check=false \
  -warmup=0 \
  -repeat=1 \
  >"${OUT_DIR}/section53_pip.stdout.txt" \
  2>"${OUT_DIR}/section53_pip.stderr.txt"

"${POLYOVER_EXEC}" \
  -poly1 "${COUNTY}" \
  -poly2 "${SOIL}" \
  -serialize="${OUT_DIR}/serialize" \
  -grid_size=15000 \
  -mode=rt \
  -v=1 \
  -fau \
  -xsect_factor=0.1 \
  -enlarge=3.5 \
  -check=false \
  -output="${OUT_DIR}/section57_overlay.txt" \
  >"${OUT_DIR}/section57_overlay.stdout.txt" \
  2>"${OUT_DIR}/section57_overlay.stderr.txt"

python3 - <<PY
import hashlib, json
from pathlib import Path
out = Path("${OUT_DIR}")
answer = Path("${ANSWER}")
generated = out / "section57_overlay.txt"

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

summary = {
    "schema": "rtdl.paper_reproduction.rayjoin.author_official_public_sample.v1",
    "query_exec": "${QUERY_EXEC}",
    "polyover_exec": "${POLYOVER_EXEC}",
    "section52_stdout": str(out / "section52_lsi.stdout.txt"),
    "section52_stderr": str(out / "section52_lsi.stderr.txt"),
    "section53_stdout": str(out / "section53_pip.stdout.txt"),
    "section53_stderr": str(out / "section53_pip.stderr.txt"),
    "section57_stdout": str(out / "section57_overlay.stdout.txt"),
    "section57_stderr": str(out / "section57_overlay.stderr.txt"),
    "section57_output": str(generated),
    "section57_answer": str(answer),
    "section57_bytes": generated.stat().st_size,
    "answer_bytes": answer.stat().st_size,
    "section57_sha256": sha(generated),
    "answer_sha256": sha(answer),
}
summary["section57_byte_equal_to_answer"] = (
    summary["section57_bytes"] == summary["answer_bytes"]
    and summary["section57_sha256"] == summary["answer_sha256"]
)
(out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
PY
