# Goal3913 Safe Next-Pod RayJoin Timing Runbook

Date: 2026-06-08

## Why This Exists

The next A5000 run should measure the Goal3909-3912 RayJoin wrapper work:

- nested LSI/overlay subprobe phase timing;
- shared loaded-case reuse inside the LSI/overlay subprobe;
- top-level representative-profile propagation of nested timing.

This runbook is also a safety guard for Windows PowerShell SSH usage: keep remote shell variables and `$(...)` expansion out of PowerShell double-quoted strings.

## Current Commit To Test

Use current `main` at or after:

`dac00448` Goal3912 propagate RayJoin subprobe timings

## Safe Remote Workspace Rule

On a fresh pod, create the workspace on the remote side only:

```bash
workdir="$(mktemp -d /root/goal3913_rayjoin.XXXXXX)"
test -n "$workdir"
test "$workdir" != "/root"
cd "$workdir"
```

Do not run `rm -rf /root/$name` from a PowerShell double-quoted SSH command.

## Recommended Remote Bash Script

Paste or pipe this script to SSH as stdin, not inside a PowerShell double-quoted command:

```bash
set -euo pipefail
echo "[goal3913] start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
workdir="$(mktemp -d /root/goal3913_rayjoin.XXXXXX)"
echo "[goal3913] workdir=$workdir"
test -n "$workdir"
test "$workdir" != "/root"
cd "$workdir"
git clone --depth 1 https://github.com/rubaolee/rtdl.git repo
cd repo
echo "[goal3913] commit=$(git rev-parse --short HEAD)"

export PYTHONPATH=/root/rtdl_goal3788_clean_1780857956/.pydeps_goal3788_numba:src:.
export RTDL_OPTIX_LIBRARY=/root/rtdl_goal3788_clean_1780857956/build/librtdl_optix.so
export RTDL_OPTIX_LIB="$RTDL_OPTIX_LIBRARY"

test -f "$RTDL_OPTIX_LIBRARY"
test -f /root/rtdl/data/rayjoin_public_cdb/br_county_start256_count512.cdb
test -f /root/rtdl/data/rayjoin_public_cdb/br_soil_start256_count512.cdb

mkdir -p /root/goal3913_rayjoin_subprobe_artifacts
timeout 900 python3 scripts/goal3866_rayjoin_representative_scale_profile.py \
  --data-dir /root/rtdl/data/rayjoin_public_cdb \
  --repeat 50 \
  --warmup 5 \
  --pip-batch-single-repeat 12 \
  --pip-batch-repeat 8 \
  --pip-batch-request-counts 1 100 \
  --output /root/goal3913_rayjoin_subprobe_artifacts/summary.json

python3 - <<'PY'
import json
p = "/root/goal3913_rayjoin_subprobe_artifacts/summary.json"
d = json.load(open(p))
print("[goal3913] gpu", d.get("gpu"))
print("[goal3913] commit", d.get("git_commit", "")[:8])
print("[goal3913] wrapper", d.get("wrapper_phase_timing_sec"))
for case in d.get("cases", []):
    print("[goal3913] case", case.get("workload"))
    print("  route", case.get("rtdl_optix_execution_route"))
    print("  reuse", case.get("loaded_case_reuse_enabled"))
    print("  subprobe", case.get("subprobe_wrapper_phase_timing_sec"))
PY
```

## Windows Invocation Pattern

Use a script file or stdin pipeline. Example pattern:

```powershell
Get-Content -Raw .\scratch\goal3913_remote.sh |
  ssh -o BatchMode=yes -o ServerAliveInterval=30 -i .\id_ed25519_rtdl_codex -p PORT root@HOST 'bash -s'
```

The single quotes around `'bash -s'` are intentional.

## Expected Evidence

The resulting JSON should include:

- `wrapper_phase_timing_sec`;
- `cases[*].subprobe_wrapper_phase_timing_sec` for LSI and overlay;
- `cases[*].loaded_case_reuse_enabled: true` for LSI and overlay;
- RTDL/OptiX execution routes ending in `_loaded_case_reuse`.

This packet is diagnostic evidence only until reviewed. It does not authorize release, RayJoin reproduction, broad RT-core speedup, whole-app speedup, or true-zero-copy claims.
