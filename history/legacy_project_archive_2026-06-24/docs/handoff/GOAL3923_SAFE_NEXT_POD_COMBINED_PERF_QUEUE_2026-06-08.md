# Goal3923 Safe Next-Pod Combined Performance Queue

Date: 2026-06-08

## Purpose

Use this when a fresh A5000-or-better pod is available. It runs the two pending
diagnostics from current main in one controlled remote session:

1. Goal3913 RayJoin LSI/overlay subprobe timing with shared loaded-case reuse.
2. Goal3920 RT-DBSCAN blocked Numba column-signature timing.

This is a runbook, not evidence by itself. Results must be reviewed before any
route promotion or performance wording.

## Windows Invocation Pattern

Write the remote script to a local file, then pipe it to SSH over stdin:

```powershell
Get-Content -Raw .\scratch\goal3923_remote.sh |
  ssh -o BatchMode=yes -o ServerAliveInterval=30 -i .\id_ed25519_rtdl_codex -p PORT root@HOST 'bash -s'
```

The single quotes around `'bash -s'` are intentional. Do not place remote
`$var` or `$(...)` expressions inside a PowerShell double-quoted SSH command.

## Remote Script

```bash
set -euo pipefail
echo "[goal3923] start $(date -u +%Y-%m-%dT%H:%M:%SZ)"

workdir="$(mktemp -d /root/goal3923_queue.XXXXXX)"
echo "[goal3923] workdir=$workdir"
test -n "$workdir"
test "$workdir" != "/root"
cd "$workdir"

git clone --depth 1 https://github.com/rubaolee/rtdl.git repo
cd repo
commit="$(git rev-parse --short HEAD)"
echo "[goal3923] commit=$commit"

export PYTHONPATH=/root/rtdl_goal3788_clean_1780857956/.pydeps_goal3788_numba:src:.
export RTDL_OPTIX_LIBRARY=/root/rtdl_goal3788_clean_1780857956/build/librtdl_optix.so
export RTDL_OPTIX_LIB="$RTDL_OPTIX_LIBRARY"

test -f "$RTDL_OPTIX_LIBRARY"
test -f /root/rtdl/data/rayjoin_public_cdb/br_county_start256_count512.cdb
test -f /root/rtdl/data/rayjoin_public_cdb/br_soil_start256_count512.cdb

artifact_root=/root/goal3923_combined_perf_artifacts
mkdir -p "$artifact_root/rayjoin" "$artifact_root/rtdbscan"
echo "$commit" > "$artifact_root/git_commit.txt"

echo "[goal3923] RayJoin subprobe begin $(date -u +%H:%M:%S)"
timeout 900 python3 scripts/goal3866_rayjoin_representative_scale_profile.py \
  --data-dir /root/rtdl/data/rayjoin_public_cdb \
  --repeat 50 \
  --warmup 5 \
  --pip-batch-single-repeat 12 \
  --pip-batch-repeat 8 \
  --pip-batch-request-counts 1 100 \
  > "$artifact_root/rayjoin/summary.json" \
  2> "$artifact_root/rayjoin/run.log"
echo "[goal3923] RayJoin subprobe done $(date -u +%H:%M:%S)"

for mode in \
  optix_rt_core_grouped_stream_numba_column_signature_3d \
  optix_rt_core_grouped_stream_blocked_numba_column_signature_3d
do
  echo "[goal3923] RTDBSCAN mode=$mode begin $(date -u +%H:%M:%S)"
  timeout 900 python3 examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py \
    --mode "$mode" \
    --dataset clustered3d \
    --point-count 65536 \
    --repeat 5 \
    --warmup 1 \
    --grouped-union-query-block-size 4096 \
    --no-validation \
    > "$artifact_root/rtdbscan/${mode}.json" \
    2> "$artifact_root/rtdbscan/${mode}.stderr.txt"
  echo "[goal3923] RTDBSCAN mode=$mode done $(date -u +%H:%M:%S)"
done

python3 - <<'PY'
import json
from pathlib import Path

root = Path("/root/goal3923_combined_perf_artifacts")
manifest = {
    "artifact_root": str(root),
    "git_commit": (root / "git_commit.txt").read_text().strip(),
    "rayjoin": {},
    "rtdbscan": [],
    "claim_boundary": {
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "app_specific_native_engine_logic_allowed": False,
    },
}

rayjoin_path = root / "rayjoin" / "summary.json"
rayjoin = json.load(open(rayjoin_path))
manifest["rayjoin"] = {
    "path": str(rayjoin_path),
    "gpu": rayjoin.get("gpu"),
    "wrapper_phase_timing_sec": rayjoin.get("wrapper_phase_timing_sec"),
    "cases": [
        {
            "workload": case.get("workload"),
            "loaded_case_reuse_enabled": case.get("loaded_case_reuse_enabled"),
            "rtdl_optix_execution_route": case.get("rtdl_optix_execution_route"),
            "subprobe_wrapper_phase_timing_sec": case.get("subprobe_wrapper_phase_timing_sec"),
        }
        for case in rayjoin.get("cases", [])
    ],
}

for path in sorted((root / "rtdbscan").glob("*.json")):
    data = json.load(open(path))
    meta = data.get("metadata", {})
    manifest["rtdbscan"].append(
        {
            "path": str(path),
            "mode": path.stem,
            "elapsed_sec": data.get("elapsed_sec"),
            "partner": meta.get("partner"),
            "path_label": meta.get("path"),
            "blocked": meta.get("grouped_union_query_blocked_candidate"),
            "block_size": meta.get("grouped_union_query_block_size"),
            "signature": meta.get("column_signature_strategy"),
        }
    )

(root / "summary_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
print(json.dumps(manifest, indent=2, sort_keys=True))
PY

echo "[goal3923] complete $(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

## Acceptance Criteria

- The script prints progress at start, before and after each diagnostic, and at
  completion.
- `summary_manifest.json` exists under
  `/root/goal3923_combined_perf_artifacts`.
- The RayJoin summary includes `wrapper_phase_timing_sec`, nested
  `subprobe_wrapper_phase_timing_sec`, and `loaded_case_reuse_enabled`.
- The RT-DBSCAN rows parse successfully, use `partner: numba`, and include both
  blocked and unblocked modes.
- All claim-boundary flags remain false.

## Non-Goals

This runbook does not install or repair OptiX, does not delete remote
workspaces, does not promote a default route, and does not authorize public
speedup, release, true-zero-copy, RayJoin reproduction, or DBSCAN paper
reproduction wording.
