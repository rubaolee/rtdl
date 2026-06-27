#!/usr/bin/env bash
set -euo pipefail

cd /root/rtdl_v3_rebuild_20260620/current

ART=/root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m5_topology_20260620
PY=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0

mkdir -p "$ART"

{
  echo "Phoenix V3 M5 topology run started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "workdir=$(pwd)"
  echo "artifact_dir=$ART"
  echo "python=$PY"

  nvidia-smi | tee "$ART/nvidia-smi.txt"
  cat VERSION | tee "$ART/source_version.txt"
  sha256sum \
    VERSION \
    src/rtdsl/v3_0_m5_topology_pilots.py \
    scripts/goal4373_rayjoin_cdb_point_location_compare.py \
    scripts/v3_0_m33_rayjoin_overlay_active_count_same_contract.py \
    scripts/v3_optix_hardware_gate.py \
    scripts/v3_phoenix_m5_topology_intake.py \
    > "$ART/source_manifest.sha256"
  cat "$ART/source_manifest.sha256"

  PYTHONPATH=src:. "$PY" scripts/v3_gpu_python_env_gate.py \
    --json-out "$ART/gpu_env_gate.json" \
    | tee "$ART/gpu_env_gate.stdout.json"

  PYTHONPATH=src:. "$PY" scripts/v3_optix_hardware_gate.py \
    --require-rt-hardware \
    --json-out "$ART/optix_hardware_gate.json" \
    --pretty \
    | tee "$ART/optix_hardware_gate.stdout.json"

  make build-embree build-optix OPTIX_PREFIX="$OPTIX_PREFIX"

  PYTHONPATH=src:. "$PY" -c \
    "import json, rtdsl as rt; print(json.dumps(rt.validate_m5_topology_pilots(), sort_keys=True))" \
    | tee "$ART/m5_local_graph_gate.json"

  : > "$ART/rayjoin_query_exec_path.txt"
  for candidate in \
    /workspace/rayjoin/build/query_exec \
    /workspace/RayJoin/build/query_exec \
    /workspace/rayjoin/build/src/query_exec \
    /workspace/RayJoin/build/src/query_exec \
    /root/rayjoin/build/query_exec \
    /root/RayJoin/build/query_exec; do
    if [[ -x "$candidate" ]]; then
      printf "%s\n" "$candidate" > "$ART/rayjoin_query_exec_path.txt"
      break
    fi
  done
  if [[ ! -s "$ART/rayjoin_query_exec_path.txt" ]] && [[ -d /workspace ]]; then
    timeout 20s find /workspace -maxdepth 6 -type f -name query_exec -print -quit \
      > "$ART/rayjoin_query_exec_path.txt" 2>/dev/null || true
  fi
  if [[ ! -s "$ART/rayjoin_query_exec_path.txt" ]] && [[ -d /root ]]; then
    timeout 20s find /root -maxdepth 5 \
      -path /root/rtdl_v3_rebuild_20260620/artifacts -prune \
      -o -type f -name query_exec -print -quit \
      > "$ART/rayjoin_query_exec_path.txt" 2>/dev/null || true
  fi
  if test -s "$ART/rayjoin_query_exec_path.txt"; then
    echo present | tee "$ART/rayjoin_query_exec_status.txt"
  else
    echo missing | tee "$ART/rayjoin_query_exec_status.txt"
  fi

  rayjoin_args=()
  if [[ "$(cat "$ART/rayjoin_query_exec_status.txt")" == "present" ]]; then
    rayjoin_args=(--rayjoin-query-exec "$(cat "$ART/rayjoin_query_exec_path.txt")")
  fi

  PYTHONPATH=src:. "$PY" scripts/goal4373_rayjoin_cdb_point_location_compare.py \
    --base-cdb data/rayjoin_public_cdb/br_county.cdb \
    --query-cdb "$ART/goal4373_query_points_parity_filtered_100k.cdb" \
    --generate-query-cdb \
    --filter-backend-parity \
    --parity-filter-oversample 2048 \
    --point-count 100000 \
    --seed 4373 \
    --rtdl-warmups 3 \
    --rtdl-repeats 1000 \
    --optix-repeats 1000 \
    --embree-repeats 1000 \
    --correctness-sample 100000 \
    --output-dir "$ART/m5_pip_point_location_parity_filtered_100k" \
    "${rayjoin_args[@]}"

  PYTHONPATH=src:. "$PY" scripts/v3_0_m33_rayjoin_overlay_active_count_same_contract.py \
    --left-cdb data/rayjoin_public_cdb/br_county_start256_count512.cdb \
    --right-cdb data/rayjoin_public_cdb/br_soil_start256_count512.cdb \
    --warmup 2 \
    --repeat 25 \
    --output "$ART/m5_overlay_active_count_same_contract.json"

  PYTHONPATH=src:. "$PY" scripts/v3_phoenix_m5_topology_intake.py \
    --artifact-dir "$ART" \
    --json-out "$ART/m5_topology_intake_summary.json" \
    --md-out "$ART/m5_topology_intake_summary.md" \
    --pretty \
    | tee "$ART/m5_topology_intake_summary.stdout.json"

  find "$ART" -maxdepth 2 -type f -printf "%P\t%s bytes\n" | sort > "$ART/artifact_file_index.txt"
  cat "$ART/artifact_file_index.txt"
  echo "Phoenix V3 M5 topology run finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} 2>&1 | tee "$ART/m5_remote_run.log"
