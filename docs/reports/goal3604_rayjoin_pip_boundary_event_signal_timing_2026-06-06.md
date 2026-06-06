# Goal3604 - RayJoin PIP Boundary-Event Signal Timing

Date: 2026-06-06

Status: internal v2.9 performance scout. This does not authorize release, public speedup wording, RayJoin paper reproduction, RTDL-beats-RayJoin, RT-core speedup, true zero-copy, or native default-route claims.

## Purpose

Goal3386/3388 showed that a generic boundary-event signal can repair the public-CDB PIP overcount problem:

1. OptiX emits generic point/closed-shape candidate device columns.
2. OptiX emits generic first-boundary-event device columns.
3. CuPy selects likely ambiguous points from candidate and strict-zero boundary-event counts.
4. CuPy filters only selected points with an explicit `crossing_tolerance`.
5. The final rows match the exact prepared OptiX oracle on 512, 1024, and 2048 chain slices.

Goal3604 asks the performance question: is that constructive route fast enough to replace the current RayJoin PIP recommendation?

## Evidence

Pod:

- NVIDIA RTX A5000, driver 580.126.09

Source:

- runner commit `7524cd565211f7e295d5f79a7028a63f7684ff84`
- artifact path `docs/reports/goal3604_rayjoin_pip_boundary_event_signal_timing_a5000/summary.json`

Command shape:

```bash
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=/root/rtdl_goal3595_clean/build/librtdl_optix.so
export RTDL_OPTIX_LIB=/root/rtdl_goal3595_clean/build/librtdl_optix.so
python3 scripts/goal3604_rayjoin_pip_boundary_event_signal_timing.py \
  --counts 512,1024,2048 \
  --repeat 20 \
  --warmup 5 \
  --output docs/reports/goal3604_rayjoin_pip_boundary_event_signal_timing_a5000/summary.json
```

The pod source status in the artifact contains only untracked runtime data and the generated artifact directory.

## Results

All three routes produce the same exact positive-membership count on every row.

| Chains | Count | CuPy Dense Sec | Prepared OptiX Exact Sec | Boundary-Event Signal Sec | Prepared OptiX / CuPy | Boundary Signal / CuPy |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 512 | 1417 | 0.000443555 | 0.000825559 | 0.012200347 | 0.537x | 0.036x |
| 1024 | 2827 | 0.000464818 | 0.001399391 | 0.016942505 | 0.332x | 0.027x |
| 2048 | 5619 | 0.000497468 | 0.002284547 | 0.021782851 | 0.218x | 0.023x |

Summary:

- all counts match,
- boundary-event signal counts match exact on all rows,
- geomean prepared OptiX exact speedup vs CuPy: `0.339x`,
- geomean boundary-event signal speedup vs CuPy: `0.028x`,
- minimum boundary-event signal speedup vs CuPy: `0.023x`.

## Phase Scout

A separate 512-chain phase scout after warmup showed the boundary-event route is not slow because of a single isolated defect. The median-ish phase costs were:

| Phase | Sec |
| --- | ---: |
| candidate device columns | 0.001209 |
| boundary-event device columns | 0.003707 |
| CuPy selected-point derivation | 0.003235 |
| CuPy selective filter | 0.002288 |
| summed route phases | 0.010432 |

This explains the result: the route is a correct multi-stage composition, but it pays multiple launches and materializes a larger boundary-event stream (`4836` boundary rows for `1429` candidate rows on the 512-chain slice).

## Interpretation

The boundary-event signal route is architecturally valuable but not a performance route today.

For current v2.9 RayJoin PIP guidance:

- recommend the CuPy dense CUDA-core scalar count for public-CDB PIP count;
- keep prepared OptiX exact count as the best no-partner RTDL/OptiX PIP count route;
- do not promote the boundary-event selective route as the default performance path.

The design lesson is precise: RTDL needs a fused generic exact closed-shape membership/count primitive if PIP scalar count must compete here. That primitive should avoid producing and reducing a large boundary-event row stream for a scalar count-only workload. It must still be app-agnostic: point id, shape id, boundary event, deterministic tolerance/tie-break, topology/owner policy columns are generic; RayJoin/CDB assignment semantics remain in Python or partner code.

## Boundary

Goal3604 is internal evidence only. It supports the v2.9 route-selection decision, not public performance wording.

It does not authorize:

- release,
- public speedup wording,
- RayJoin paper reproduction,
- RTDL-beats-RayJoin,
- broad RT-core speedup,
- true zero-copy,
- native default-route promotion.
