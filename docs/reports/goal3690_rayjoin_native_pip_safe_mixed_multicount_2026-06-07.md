# Goal3690 RayJoin Native-PIP Safe Mixed Multi-Count Sweep

Date: 2026-06-07

## Purpose

Goal3688 measured the native-PIP safe mixed RayJoin count candidate at one `4096`-chain packet. Goal3690 broadens that same route to a small count-scale sweep so the result is not anchored to one size.

No implementation changed for Goal3690. It reuses:

- `scripts/goal3688_rayjoin_native_pip_safe_mixed_composite.py`
- PIP: native resident relation-status corrected scalar count,
- LSI: existing exact prepared RTDL/OptiX route with host double refinement,
- overlay seed: existing RTDL/OptiX active-count route.

## A5000 Evidence

Artifact:

`docs/reports/goal3690_rayjoin_native_pip_safe_mixed_multicount_a5000/summary.json`

Pod:

- GPU: `NVIDIA RTX A5000, 580.126.09`
- source commit: `9cfbc20d`
- `goal3688_scoped_source_dirty=false`
- OptiX library: `/root/rtdl/build/librtdl_optix.so`
- point primitive predicate epsilon: `1e-9`

Run shape:

- counts: `512,1024,2048,4096`
- `repeat=10`
- `warmup=3`

## Results

All rows matched the dense all-CuPy same-contract baseline.

| Chain count | Dense all-CuPy sum median (s) | Candidate sum median (s) | Candidate speedup |
| ---: | ---: | ---: | ---: |
| `512` | `0.073661895` | `0.001463914` | `50.318x` |
| `1024` | `0.164915382` | `0.001509481` | `109.253x` |
| `2048` | `0.357091631` | `0.005535653` | `64.508x` |
| `4096` | `1.431855434` | `0.006025550` | `237.631x` |

Summary:

- geomean candidate speedup versus dense all-CuPy: `95.812x`,
- minimum candidate speedup: `50.318x`,
- all count rows match: `true`.

Per-workload speedups:

| Chain count | PIP | LSI | overlay seed |
| ---: | ---: | ---: | ---: |
| `512` | `1.288x` | `68.548x` | `63.179x` |
| `1024` | `1.265x` | `225.114x` | `104.262x` |
| `2048` | `1.376x` | `320.728x` | `20.435x` |
| `4096` | `2.333x` | `899.113x` | `38.433x` |

## Interpretation

The multi-count sweep strengthens Goal3688's limited conclusion:

- the candidate composite remains exact for every measured count,
- the native-PIP leg is consistently faster than the dense all-CuPy PIP baseline,
- the composite speedup is dominated by LSI and overlay avoiding dense all-pairs CuPy work,
- the result remains a candidate internal route, not public RayJoin paper-reproduction evidence.

The PIP leg itself is no longer the huge bottleneck for this candidate route. It is faster than the dense all-CuPy baseline but only by about `1.27x-2.33x` across this sweep. Further large RayJoin gains should focus on the remaining route-level benchmark contract and on paper-code comparison, not more tiny PIP scalar tuning.

## Boundary

This report does not authorize:

- release,
- default-route promotion,
- public speedup claims,
- RTDL-beats-RayJoin claims,
- RayJoin paper reproduction claims,
- broad RT-core speedup claims,
- true zero-copy claims.

Goal3690 only records additional internal evidence that the Goal3688 candidate route is exact and faster than dense all-CuPy across the measured public-CDB count sizes.
