# Goal3920 Safe Next-Pod RT-DBSCAN Blocked Numba Runbook

Date: 2026-06-08

## Purpose

Goal3918 added blocked grouped-stream Numba modes for RT-DBSCAN. The next A5000 run should compare the current unblocked Numba column-signature route against the new blocked Numba column-signature route under the same protocol.

## Current Commit To Test

Use current `main` at or after:

`1018719b` Goal3918 add RTDBSCAN blocked Numba modes

## Safe Remote Workspace Rule

Create the workspace on the remote side:

```bash
workdir="$(mktemp -d /root/goal3920_rtdbscan.XXXXXX)"
test -n "$workdir"
test "$workdir" != "/root"
cd "$workdir"
```

Do not run remote `$(...)`, `$var`, or `rm -rf /root/$name` inside a PowerShell double-quoted SSH command.

## Recommended Remote Bash Script

Pipe this script to SSH as stdin:

```bash
set -euo pipefail
echo "[goal3920] start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
workdir="$(mktemp -d /root/goal3920_rtdbscan.XXXXXX)"
echo "[goal3920] workdir=$workdir"
test -n "$workdir"
test "$workdir" != "/root"
cd "$workdir"
git clone --depth 1 https://github.com/rubaolee/rtdl.git repo
cd repo
echo "[goal3920] commit=$(git rev-parse --short HEAD)"

export PYTHONPATH=/root/rtdl_goal3788_clean_1780857956/.pydeps_goal3788_numba:src:.
export RTDL_OPTIX_LIBRARY=/root/rtdl_goal3788_clean_1780857956/build/librtdl_optix.so
export RTDL_OPTIX_LIB="$RTDL_OPTIX_LIBRARY"
test -f "$RTDL_OPTIX_LIBRARY"

mkdir -p /root/goal3920_rtdbscan_blocked_numba_artifacts

for mode in \
  optix_rt_core_grouped_stream_numba_column_signature_3d \
  optix_rt_core_grouped_stream_blocked_numba_column_signature_3d
do
  echo "[goal3920] running $mode"
  timeout 900 python3 examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py \
    --mode "$mode" \
    --dataset clustered3d \
    --point-count 65536 \
    --repeat 5 \
    --warmup 1 \
    --grouped-union-query-block-size 4096 \
    --no-validation \
    > "/root/goal3920_rtdbscan_blocked_numba_artifacts/${mode}.json" \
    2> "/root/goal3920_rtdbscan_blocked_numba_artifacts/${mode}.stderr.txt"
done

python3 - <<'PY'
import json
from pathlib import Path
root = Path("/root/goal3920_rtdbscan_blocked_numba_artifacts")
for path in sorted(root.glob("*.json")):
    data = json.load(open(path))
    meta = data.get("metadata", {})
    timing = meta.get("benchmark_timing_breakdown", {})
    print("[goal3920]", path.name)
    print("  elapsed_sec", data.get("elapsed_sec"))
    print("  path", meta.get("path"))
    print("  partner", meta.get("partner"))
    print("  blocked", meta.get("grouped_union_query_blocked_candidate"))
    print("  block_size", meta.get("grouped_union_query_block_size"))
    print("  signature", meta.get("column_signature_strategy"))
    print("  derived", timing.get("derived_sec"))
PY
```

## Acceptance For This Diagnostic

The diagnostic passes only if both JSON files:

- parse successfully;
- report `partner: numba`;
- report matching signatures;
- keep all claim authorization flags false;
- show the blocked row metadata as `grouped_union_query_blocked_candidate: true`.

Do not promote the blocked Numba route unless it wins timing on the A5000 packet and keeps signature stability.
