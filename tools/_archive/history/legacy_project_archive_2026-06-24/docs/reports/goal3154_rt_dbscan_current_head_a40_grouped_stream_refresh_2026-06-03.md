# Goal3154: RT-DBSCAN Current-Head A40 Grouped-Stream Refresh

Date: 2026-06-03

Status: `pass`

## Purpose

Goal3154 refreshes the current RT-DBSCAN benchmark evidence after the v2.8 front-door adoption and compact-mask hardening work. This is not a new release gate and not a new public claim. It is a current-head measurement packet used to guide the next generic runtime primitive work.

The measured row is the existing live grouped-stream harness:

- prepared CuPy grid components as the same-contract CUDA-core opponent;
- prepared RTDL/OptiX count-threshold plus CuPy grid continuation;
- RTDL/OptiX grouped-stream continuation that avoids neighbor-row materialization and avoids a full directed adjacency stream.

## Pod Environment

```text
Pod SSH: ssh root@69.30.85.131 -p 22063 -i id_ed25519_rtdl_codex
GPU: NVIDIA A40
Driver: 570.211.01
Python: /root/venvs/rtdl_goal3154/bin/python
CuPy: 14.1.1
Numba: 0.65.1
CUDA nvcc: Build cuda_12.8.r12.8/compiler.35583870_0
OptiX SDK: /root/vendor/optix-sdk, tag v8.0.0
RTDL OptiX library: /root/rtdl_goal3151/build/librtdl_optix.so
Source commit: e38a90db634ad0b911f7857a3b2b8cea588cb529
Source dirty: []
```

## Command

```bash
cd /root/rtdl_goal3151
git fetch origin main
git reset --hard origin/main
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
export PATH=/usr/local/cuda-12.8/bin:$PATH
timeout 1800s /root/venvs/rtdl_goal3154/bin/python \
  scripts/goal2802_rt_dbscan_v25_live_grouped_stream_harness.py \
  --point-count 32768 \
  --point-count 65536 \
  --point-count 131072 \
  --repeat-count 3 \
  --raw-output-dir /tmp/goal3154_rt_dbscan_raw_clean \
  --output /tmp/goal3154_rt_dbscan_current_head_a40_clean.json
```

Artifact:

- `docs/reports/goal3154_pod_artifacts/rt_dbscan_current_head_a40_clean.json`

## Results

| Points | Prepared CuPy Grid Tail Median (s) | RT Count + Prepared Grid Tail Median (s) | RT Count Speedup | Grouped Stream Tail Median (s) | Grouped Native Tail Median (s) | Grouped Speedup | Planned Continuation | Status |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 32,768 | 0.152594 | 0.142105 | 1.074x | 0.036984 | 0.024058 | 4.126x | full adjacency fits | pass |
| 65,536 | 0.450711 | 0.329298 | 1.369x | 0.091914 | 0.066502 | 4.904x | grouped stream | pass |
| 131,072 | 1.440565 | 0.937694 | 1.536x | 0.278144 | 0.227305 | 5.179x | grouped stream | pass |

Artifact checks:

- `status`: `pass`
- signatures match across prepared CuPy grid, RT count bridge, and grouped stream
- grouped stream uses RT cores
- grouped stream avoids neighbor-row materialization
- grouped stream avoids a full directed adjacency stream
- minimum grouped-stream speedup vs prepared CuPy grid: `4.125981x`
- maximum grouped-stream speedup vs prepared CuPy grid: `5.179199x`

## Design Takeaway

The current RT-DBSCAN path is already strong for the v2.8 benchmark row. The grouped-stream path is generic, uses RT traversal, avoids the two large materialization costs, and beats the same-contract prepared CuPy grid opponent on the clustered3d stress row.

The next useful engineering step is not another one-off DBSCAN app wrapper. It is to promote the successful shape into a v2.8-discoverable generic front-door contract for fixed-radius graph/component continuation:

- typed adjacency stream or grouped-stream producer metadata;
- explicit user-selected partner continuation;
- component-label output contract;
- no `dbscan`, `cluster`, or `min_neighbors` vocabulary in native/runtime layers;
- claim boundary still blocked unless a later release packet authorizes it.

## Claim Boundary

- `public_speedup_claim_authorized: False`
- `whole_app_speedup_claim_authorized: False`
- `paper_reproduction_claim_authorized: False`
- `paper_speedup_claim_authorized: False`
- `broad_dbscan_speedup_claim_authorized: False`
- `pure_triton_components_claim_authorized: False`
- `native_engine_customization: False`
- `release_authorized: False`

