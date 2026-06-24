# Goal1619 v1.6.4 Linux Packet Runner Rehearsal

Date: 2026-05-09

## Verdict

ACCEPTED as local Linux all-backend packet-runner rehearsal.

This is GTX 1070 behavior evidence only. It is not representative RTX
performance evidence and does not authorize public speedup wording, true
zero-copy wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording,
release tags, or release action.

## Environment

- Host: `192.168.1.20`
- Linux hostname: `lx1`
- Checkout: `/home/lestat/work/rtdl_codex_local_check`
- Git commit: `effa1a5ada355d13a2517b27a9122a110a100599`
- GPU: `NVIDIA GeForce GTX 1070`
- Driver: `580.126.09`
- GPU memory: `8192 MiB`

## Command

```bash
PYTHONPATH=src:. LD_LIBRARY_PATH=$PWD/build:$LD_LIBRARY_PATH \
python3 scripts/goal1618_v1_6_4_collect_k_packet_runner.py \
  --environment-label linux_gtx1070_all_backend_packet_rehearsal \
  --backends fake_native embree optix \
  --required-backends fake_native embree optix \
  --json-out docs/reports/goal1618_v1_6_4_linux_all_backend_packet_runner_2026-05-09.json \
  --md-out docs/reports/goal1618_v1_6_4_linux_all_backend_packet_runner_2026-05-09.md
```

## Outcome

- Packet status: `accepted_packet_execution`
- Packet accepted: `true`
- Backends: `fake_native`, `embree`, `optix`
- Required backends: `fake_native`, `embree`, `optix`
- Failed subpackages: none
- Goal1614 bounds stress subpackage: accepted
- Goal1615 reduced-copy benchmark subpackage: accepted

## Artifacts

- `docs/reports/goal1618_v1_6_4_linux_all_backend_packet_runner_2026-05-09.json`
- `docs/reports/goal1618_v1_6_4_linux_all_backend_packet_runner_2026-05-09.md`

## Claim Boundary

This rehearsal validates that the single Goal1618 packet runner can execute the
required-backend collect-k packet on local Linux. It does not satisfy the
representative RTX packet requirement, does not prove public performance
wording, and does not authorize stable promotion or release action.
