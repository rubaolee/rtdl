#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "${APP_DIR}/../.." && pwd)"
DATA_DIR="${RAYJOIN_DATA_DIR:-${APP_DIR}/_data/public_sample}"
OUT_DIR="${RAYJOIN_OUT_DIR:-${APP_DIR}/_runs/public_sample/rtdl}"
CACHE_DIR="${RAYJOIN_CACHE_DIR:-${APP_DIR}/_runs/public_sample/cache}"
OPTIX_PREFIX="${OPTIX_PREFIX:-${HOME}/vendor/optix-dev}"
CUDA_PREFIX="${CUDA_PREFIX:-/usr/lib/cuda}"

COUNTY="${DATA_DIR}/br_county_clean_25_odyssey_final.txt"
SOIL="${DATA_DIR}/br_soil_ascii_odyssey_final.txt"
ANSWER="${DATA_DIR}/br_countyXbr_soil_answer.txt"

mkdir -p "${OUT_DIR}" "${CACHE_DIR}"

cd "${REPO_ROOT}"
if [ ! -f build/librtdl_optix.so ]; then
  make build-optix OPTIX_PREFIX="${OPTIX_PREFIX}" CUDA_PREFIX="${CUDA_PREFIX}"
fi

export PYTHONPATH=src:.
export RTDL_OPTIX_LIB="${REPO_ROOT}/build/librtdl_optix.so"
export RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR="${CACHE_DIR}"

python3 Paper-reproduction-apps/rayjoin-paper/section52_lsi.py \
  --poly1 "${COUNTY}" \
  --poly2 "${SOIL}" \
  --label br_county_soil \
  --output "${OUT_DIR}/section52_lsi.json"

python3 Paper-reproduction-apps/rayjoin-paper/section53_pip.py \
  --poly1 "${COUNTY}" \
  --poly2 "${SOIL}" \
  --label br_county_soil \
  --output "${OUT_DIR}/section53_pip.json" \
  --chunk-size 500000

python3 Paper-reproduction-apps/rayjoin-paper/section57_overlay.py \
  --left "${COUNTY}" \
  --right "${SOIL}" \
  --pair-name br_county_soil \
  --dataset-label available_bounded_pair \
  --output "${OUT_DIR}/section57_overlay.txt" \
  --author-output "${ANSWER}" \
  --summary "${OUT_DIR}/section57_overlay.json" \
  --cache-dir "${CACHE_DIR}"

python3 Paper-reproduction-apps/rayjoin-paper/section57_overlay_numba.py \
  --left "${COUNTY}" \
  --right "${SOIL}" \
  --pair-name br_county_soil \
  --dataset-label available_bounded_pair \
  --output "${OUT_DIR}/section57_overlay_numba.txt" \
  --author-output "${ANSWER}" \
  --summary "${OUT_DIR}/section57_overlay_numba.json" \
  --cache-dir "${CACHE_DIR}"

python3 - <<PY
import json
from pathlib import Path
out = Path("${OUT_DIR}")
summary = {
    "schema": "rtdl.paper_reproduction.rayjoin.rtdl_public_sample_run.v1",
    "section52": json.loads((out / "section52_lsi.json").read_text()),
    "section53": json.loads((out / "section53_pip.json").read_text()),
    "section57": json.loads((out / "section57_overlay.json").read_text()),
    "section57_numba": json.loads((out / "section57_overlay_numba.json").read_text()),
}
summary["section57_byte_equal"] = bool(summary["section57"]["byte_equal_to_author"])
summary["section57_numba_byte_equal"] = bool(summary["section57_numba"]["byte_equal_to_author"])
(out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps({
    "schema": summary["schema"],
    "section52_count": summary["section52"]["count"],
    "section53_positive_faces": summary["section53"]["section53_positive_faces"],
    "section57_byte_equal": summary["section57_byte_equal"],
    "section57_numba_byte_equal": summary["section57_numba_byte_equal"],
}, indent=2))
PY
