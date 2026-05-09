# Goal1616 v1.6.4 Collect-K RTX Packet Plan

Date: 2026-05-09

## Verdict

READY as a prepared RTX packet plan, not yet accepted as representative RTX
evidence.

The local Linux rehearsal passed with all required backends on `192.168.1.20`,
but that host has a `NVIDIA GeForce GTX 1070`. This is behavior rehearsal only,
not representative RTX performance evidence and not public speedup evidence.

## Local Linux Rehearsal

- Host: `192.168.1.20`
- Linux hostname: `lx1`
- Checkout: `/home/lestat/work/rtdl_codex_local_check`
- Git commit: `6b15aee44962c473bf3da7cebbbf7dcfb12a8c50`
- GPU: `NVIDIA GeForce GTX 1070`
- Driver: `580.126.09`
- GPU memory: `8192 MiB`
- Embree runtime probe: `(4, 3, 0)`
- OptiX runtime probe: `(9, 0, 0)`

Commands rehearsed:

```bash
PYTHONPATH=src:. LD_LIBRARY_PATH=/home/lestat/work/rtdl_codex_local_check/build:$LD_LIBRARY_PATH \
python3 scripts/goal1614_v1_6_4_collect_k_bounds_stress.py \
  --backends fake_native embree optix \
  --required-backends fake_native embree optix \
  --json-out docs/reports/goal1614_v1_6_4_linux_all_backend_bounds_stress_2026-05-09.json \
  --md-out docs/reports/goal1614_v1_6_4_linux_all_backend_bounds_stress_2026-05-09.md

PYTHONPATH=src:. LD_LIBRARY_PATH=/home/lestat/work/rtdl_codex_local_check/build:$LD_LIBRARY_PATH \
python3 scripts/goal1615_v1_6_4_collect_k_reduced_copy_benchmark.py \
  --backends fake_native embree optix \
  --required-backends fake_native embree optix \
  --json-out docs/reports/goal1615_v1_6_4_linux_all_backend_reduced_copy_benchmark_2026-05-09.json \
  --md-out docs/reports/goal1615_v1_6_4_linux_all_backend_reduced_copy_benchmark_2026-05-09.md
```

Rehearsal outcome:

- Goal1614 all-backend bounds stress: `accepted=true`
- Goal1615 all-backend reduced-copy benchmark: `accepted=true`
- Required backend skips: none
- Failed records: none

Imported rehearsal artifacts:

- `docs/reports/goal1614_v1_6_4_linux_all_backend_bounds_stress_2026-05-09.json`
- `docs/reports/goal1614_v1_6_4_linux_all_backend_bounds_stress_2026-05-09.md`
- `docs/reports/goal1615_v1_6_4_linux_all_backend_reduced_copy_benchmark_2026-05-09.json`
- `docs/reports/goal1615_v1_6_4_linux_all_backend_reduced_copy_benchmark_2026-05-09.md`

## Pod Packet

When a representative RTX pod is available, validate from Git and run this
packet from a clean checkout at current `origin/main`.

Environment preflight:

```bash
set -euo pipefail
cd /root/work/rtdl
git fetch origin main
git checkout main
git merge --ff-only origin/main
git rev-parse HEAD
hostname
nvidia-smi
python3 --version
nvcc --version || true
test -d /root/vendor/optix-sdk || test -d /opt/optix
```

Build or verify native libraries:

```bash
make build-embree
make build-optix OPTIX_PREFIX="${OPTIX_PREFIX:-/root/vendor/optix-sdk}"
test -f build/librtdl_embree.so
test -f build/librtdl_optix.so
```

Run the required-backend packet:

```bash
export PYTHONPATH=src:.
export LD_LIBRARY_PATH="$PWD/build:$LD_LIBRARY_PATH"
export RTDL_OPTIX_LIB="$PWD/build/librtdl_optix.so"

python3 -m unittest \
  tests.goal1614_v1_6_4_collect_k_bounds_stress_test \
  tests.goal1615_v1_6_4_collect_k_reduced_copy_benchmark_test \
  tests.goal1613_v1_6_4_collect_k_bounded_promotion_gate_test

python3 scripts/goal1614_v1_6_4_collect_k_bounds_stress.py \
  --backends fake_native embree optix \
  --required-backends fake_native embree optix \
  --json-out docs/reports/goal1614_v1_6_4_rtx_required_backend_bounds_stress_$(date +%Y-%m-%d).json \
  --md-out docs/reports/goal1614_v1_6_4_rtx_required_backend_bounds_stress_$(date +%Y-%m-%d).md

python3 scripts/goal1615_v1_6_4_collect_k_reduced_copy_benchmark.py \
  --backends fake_native embree optix \
  --required-backends fake_native embree optix \
  --json-out docs/reports/goal1615_v1_6_4_rtx_required_backend_reduced_copy_benchmark_$(date +%Y-%m-%d).json \
  --md-out docs/reports/goal1615_v1_6_4_rtx_required_backend_reduced_copy_benchmark_$(date +%Y-%m-%d).md
```

Acceptance rule:

- All required backends must pass: `fake_native`, `embree`, and `optix`.
- Required backend skips are blockers.
- Failed records are blockers.
- Timing fields remain diagnostic unless a later same-contract performance
  package explicitly promotes them after 3-AI review.
- RTX evidence from this packet can satisfy representative backend execution
  evidence, but cannot by itself authorize stable `COLLECT_K_BOUNDED`
  promotion.

## Claim Boundary

This packet plan and the local Linux rehearsal do not authorize stable
`COLLECT_K_BOUNDED` promotion, public speedup wording, true zero-copy wording,
whole-app speedup claims, broad RTX/GPU wording, release tags, or release
action.

Short form: no release action is authorized by this packet plan.
