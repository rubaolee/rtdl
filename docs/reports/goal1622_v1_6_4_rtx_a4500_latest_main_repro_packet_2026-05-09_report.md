# Goal1622 v1.6.4 RTX A4500 Latest-Main Repro Packet

Date: 2026-05-09

## Verdict

ACCEPTED as latest-main reproducibility evidence for the v1.6.4 collect-k
required-backend packet.

This is not public speedup evidence, not true zero-copy evidence, not stable
`COLLECT_K_BOUNDED` promotion, and not release action.

## Environment

- Pod SSH endpoint: `root@213.173.108.199 -p 18169`
- Checkout: `/root/work/rtdl`
- Git commit: `6fde3868de2525414d9902afcbc9d24b64831113`
- Hostname: `20935c812199`
- GPU: `NVIDIA RTX A4500`
- Driver: `550.127.05`
- GPU memory: `20470 MiB`
- CUDA used for existing build: `/usr/local/cuda-12.4`
- OptiX runtime library: `build/librtdl_optix.so`
- Embree runtime library: `build/librtdl_embree.so`

## Command

```bash
git fetch origin main
git reset --hard origin/main

export PYTHONPATH=src:.
export LD_LIBRARY_PATH=$PWD/build:${LD_LIBRARY_PATH:-}
export RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so

python3 scripts/goal1618_v1_6_4_collect_k_packet_runner.py \
  --environment-label representative_rtx_a4500_latest_main_repro_packet \
  --backends fake_native embree optix \
  --required-backends fake_native embree optix \
  --json-out docs/reports/goal1622_v1_6_4_rtx_a4500_latest_main_repro_packet_2026-05-09.json \
  --md-out docs/reports/goal1622_v1_6_4_rtx_a4500_latest_main_repro_packet_2026-05-09.md
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

- `docs/reports/goal1622_v1_6_4_rtx_a4500_latest_main_repro_packet_2026-05-09.json`
- `docs/reports/goal1622_v1_6_4_rtx_a4500_latest_main_repro_packet_2026-05-09.md`

## Claim Boundary

Goal1622 strengthens the evidence chain by proving that the pushed GitHub
`main` state can reproduce the representative RTX A4500 required-backend
packet. It does not authorize public speedup wording, true zero-copy wording,
whole-app speedup claims, broad RTX/GPU wording, stable `COLLECT_K_BOUNDED`
promotion, release tags, or release action.

Stable promotion remains blocked until a separate stable-promotion decision
package and 3-AI consensus explicitly accepts it.
