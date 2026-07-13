#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_ROOT="${RAYJOIN_RUN_ROOT:-${APP_DIR}/_runs/public_sample}"
DATA_DIR="${RAYJOIN_DATA_DIR:-${APP_DIR}/_data/public_sample}"

mkdir -p "${RUN_ROOT}"

python3 "${APP_DIR}/scripts/fetch_public_sample.py" --data-dir "${DATA_DIR}"

if [ "${RUN_AUTHOR:-1}" = "1" ]; then
  AUTHOR_SRC_DIR="${RAYJOIN_AUTHOR_SRC_DIR:-${APP_DIR}/_work/author_official/RayJoin}"
  AUTHOR_BUILD_DIR="${RAYJOIN_AUTHOR_BUILD_DIR:-${APP_DIR}/_work/author_official/release}"
  if [ ! -x "${AUTHOR_BUILD_DIR}/bin/polyover_exec" ]; then
    bash "${APP_DIR}/scripts/setup_author_official.sh" >"${RUN_ROOT}/author_setup.log" 2>&1
  fi
  python3 - "${RUN_ROOT}" "${AUTHOR_SRC_DIR}" "${AUTHOR_BUILD_DIR}" "${RAYJOIN_CUDA_ARCH:-}" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

run_root = Path(sys.argv[1])
src_dir = Path(sys.argv[2])
build_dir = Path(sys.argv[3])
cuda_arch = sys.argv[4]
commit = subprocess.check_output(["git", "-C", str(src_dir), "rev-parse", "HEAD"], text=True).strip()
payload = {
    "schema": "rtdl.paper_reproduction.rayjoin.author_official_setup.v1",
    "source": str(src_dir),
    "build": str(build_dir),
    "commit": commit,
    "cuda_arch": cuda_arch or "auto_or_cached",
    "query_exec": str(build_dir / "bin" / "query_exec"),
    "polyover_exec": str(build_dir / "bin" / "polyover_exec"),
    "setup_log": str(run_root / "author_setup.log"),
}
(run_root / "author_setup.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY
  RAYJOIN_DATA_DIR="${DATA_DIR}" \
  RAYJOIN_OUT_DIR="${RUN_ROOT}/author_official" \
    bash "${APP_DIR}/scripts/run_author_public_sample.sh"
else
  echo "[run-full] RUN_AUTHOR=0, skipping AuthorOfficial binary run"
fi

RAYJOIN_DATA_DIR="${DATA_DIR}" \
RAYJOIN_OUT_DIR="${RUN_ROOT}/rtdl" \
RAYJOIN_CACHE_DIR="${RUN_ROOT}/cache" \
  bash "${APP_DIR}/scripts/run_rtdl_public_sample.sh"

python3 - <<PY
import json
from pathlib import Path
root = Path("${RUN_ROOT}")
payload = {"schema": "rtdl.paper_reproduction.rayjoin.full_public_sample_run.v1"}
author = root / "author_official" / "summary.json"
rtdl = root / "rtdl" / "summary.json"
payload["author_official"] = json.loads(author.read_text()) if author.exists() else None
payload["rtdl"] = json.loads(rtdl.read_text())
payload["checks"] = {
    "rtdl_section57_byte_equal": payload["rtdl"]["section57_byte_equal"],
    "rtdl_section57_numba_byte_equal": payload["rtdl"]["section57_numba_byte_equal"],
    "author_section57_byte_equal": None if payload["author_official"] is None else payload["author_official"]["section57_byte_equal_to_answer"],
}
(root / "full_summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(json.dumps(payload["checks"], indent=2))
PY
