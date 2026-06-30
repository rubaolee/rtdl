# Goal1620 v1.6.4 RTX A4500 Collect-K Packet Evidence

Date: 2026-05-09

## Verdict

ACCEPTED as representative RTX required-backend packet-execution evidence.

This is not public speedup evidence, not true zero-copy evidence, not stable
`COLLECT_K_BOUNDED` promotion, and not release action.

## Environment

- Pod SSH endpoint: `root@213.173.108.199 -p 18169`
- Checkout: `/root/work/rtdl`
- Git commit: `a0dcb56cc2f727774a6abcb6e25bcf746ece9d78`
- Hostname: `20935c812199`
- OS: Ubuntu 22.04 container on Linux `6.8.0-45-generic`
- GPU: `NVIDIA RTX A4500`
- Driver: `550.127.05`
- GPU memory: `20470 MiB`
- CUDA used for build: `/usr/local/cuda-12.4`
- OptiX SDK: `/root/vendor/optix-sdk`, tag `v8.0.0`
- Embree package: Ubuntu `libembree-dev`, runtime probe `(3, 12, 2)`
- OptiX runtime probe: `(8, 0, 0)`

Installed pod dependencies:

- `libembree-dev`
- `libgeos-dev`
- `pkg-config`

## Build

```bash
make build-embree
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.4
```

Built artifacts:

- `build/librtdl_embree.so`
- `build/librtdl_optix.so`

## Packet Command

```bash
export PYTHONPATH=src:.
export LD_LIBRARY_PATH=$PWD/build:$LD_LIBRARY_PATH
export RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so

python3 scripts/goal1618_v1_6_4_collect_k_packet_runner.py \
  --environment-label representative_rtx_a4500_required_backend_packet \
  --backends fake_native embree optix \
  --required-backends fake_native embree optix \
  --json-out docs/reports/goal1618_v1_6_4_rtx_a4500_required_backend_packet_2026-05-09.json \
  --md-out docs/reports/goal1618_v1_6_4_rtx_a4500_required_backend_packet_2026-05-09.md
```

## Outcome

- Packet status: `accepted_packet_execution`
- Packet accepted: `true`
- Backends: `fake_native`, `embree`, `optix`
- Required backends: `fake_native`, `embree`, `optix`
- Failed subpackages: none
- Goal1614 bounds stress subpackage: accepted
- Goal1615 reduced-copy/materialization-count benchmark subpackage: accepted
- Timing remains diagnostic only.

Imported artifacts:

- `docs/reports/goal1618_v1_6_4_rtx_a4500_required_backend_packet_2026-05-09.json`
- `docs/reports/goal1618_v1_6_4_rtx_a4500_required_backend_packet_2026-05-09.md`

## Claim Boundary

Goal1620 satisfies the representative RTX required-backend packet-execution
evidence item for the v1.6.4 collect-k chain. It does not authorize public
speedup wording, true zero-copy wording, whole-app speedup claims, broad
RTX/GPU wording, stable `COLLECT_K_BOUNDED` promotion, release tags, or release
action.

Stable promotion remains blocked until a separate stable-promotion review and
3-AI consensus explicitly accepts it.
