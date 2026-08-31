#!/usr/bin/env bash
set -euo pipefail

# Populate the installed V4 callback-leaf cache by exercising every canonical
# Paper-App prepare/execute path once on bounded functional inputs.  Real-scale
# correctness/capacity is a separate gate; repeating 60M-row RayDB here would
# add memory risk without compiling a different callback leaf.

SOURCE_ROOT=${SOURCE_ROOT:?}
OUTPUT_ROOT=${OUTPUT_ROOT:?}
PYTHON=${PYTHON:?}
NATIVE=${NATIVE:?}
OPTIX_INCLUDE=${OPTIX_INCLUDE:?}
CUDA_INCLUDE=${CUDA_INCLUDE:?}

if [[ -e "${OUTPUT_ROOT}" ]]; then
  echo "refusing to replace Goal5776 canonical-path cache root" >&2
  exit 2
fi
mkdir "${OUTPUT_ROOT}"
mkdir "${OUTPUT_ROOT}/cache"

export PYTHONPATH="${SOURCE_ROOT}/src:${SOURCE_ROOT}/scripts:${SOURCE_ROOT}"
export RTDL_OPTIX_LIB="${NATIVE}"
export RTDL_OPTIX_LIBRARY="${NATIVE}"
export RTDL_V4_FORMAL_LEAF_CACHE="${OUTPUT_ROOT}/cache"
unset RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST
unset RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST_SHA256

run() {
  local label=$1
  local script=$2
  shift 2
  printf 'START %s\n' "${label}"
  "${PYTHON}" "${SOURCE_ROOT}/scripts/${script}" "$@" \
    --output "${OUTPUT_ROOT}/${label}"
  printf 'PASS %s\n' "${label}"
}

# Triangle Counting + RayDB.
run triangle_reduction goal5773_home_triangle_reduction_lifecycle_validation.py \
  --native "${NATIVE}" --optix-include "${OPTIX_INCLUDE}" \
  --cuda-include "${CUDA_INCLUDE}"

# Particle Tracking + LibRTS + RayJoin.
run particle_relation goal5773_home_particle_relation_lifecycle_validation.py \
  --native "${NATIVE}" --optix-include "${OPTIX_INCLUDE}" \
  --cuda-include "${CUDA_INCLUDE}"

# RT-BarnesHut.
run hierarchy goal5773_home_hierarchy_lifecycle_validation.py \
  --native "${NATIVE}"

# RTNN + RT-DBSCAN + X-HD.
run multiround goal5773_home_multiround_lifecycle_validation.py \
  --native "${NATIVE}" --optix-include "${OPTIX_INCLUDE}" \
  --cuda-include "${CUDA_INCLUDE}"

"${PYTHON}" - "${OUTPUT_ROOT}" <<'PY'
from __future__ import annotations

import json
from pathlib import Path
import sys

from rtdsl.v4_callback_numba_codegen import (
    materialize_formal_numba_leaf_cache_manifest,
)

root = Path(sys.argv[1])
expected_record_counts = {
    "triangle_reduction": 6,
    "particle_relation": 12,
    "hierarchy": 4,
    "multiround": 6,
}
for label, expected_count in expected_record_counts.items():
    document = json.loads((root / label / "RESULT.json").read_text())
    rows = document.get("records")
    if not isinstance(rows, list) or len(rows) != expected_count:
        raise RuntimeError(f"{label}: missing lifecycle records")
    for row in rows:
        if row.get("matched") is not True:
            raise RuntimeError(f"{label}: non-passing lifecycle record")
        successful = int(row.get("successful_launch_count", 0))
        if (
            row.get("physical_executor_classification")
            != "optix_traversal_observed"
            or successful <= 0
            or int(row.get("complete_context_launch_count", -1)) != successful
            or any(int(row.get(name, -1)) != 0 for name in (
                "failed_launch_count", "incomplete_context_launch_count",
                "pending_context_at_finish", "session_error"
            ))
        ):
            raise RuntimeError(f"{label}: invalid behavioral OptiX receipt")

manifest_path = root / "MANIFEST.json"
materialize_formal_numba_leaf_cache_manifest(
    root / "cache", manifest_path
)
manifest = json.loads(manifest_path.read_text())
import hashlib
summary = {
    "schema": "rtdl.goal5776.home_canonical_path_leaf_cache_population.v1",
    "status": "passed",
    "paper_app_count": 9,
    "canonical_execution_count": sum(expected_record_counts.values()),
    "cache_entry_count": int(manifest["entry_count"]),
    "cache_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
    "real_scale_correctness_reexecuted": False,
    "reason_real_scale_not_reexecuted": (
        "callback leaf identity depends on verified callback IR, ABI, target and "
        "toolchain, not application row count; real-scale correctness is a separate gate"
    ),
    "registered_performance_observation_created": False,
}
(root / "SUMMARY.json").write_text(
    json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n"
)
print(json.dumps(summary, sort_keys=True))
PY

chmod -R a-w "${OUTPUT_ROOT}/cache"
printf 'SEALED %s\n' "${OUTPUT_ROOT}/MANIFEST.json"
