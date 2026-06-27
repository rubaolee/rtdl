# Goal4447 / V3.0 M51 Current Benchmark Adequacy Refresh

Status: `accept-with-boundary`

M51 updates the `rtdsl.current_benchmark_adequacy()` advisory surface so it no
longer reports the old v2.10/Goal3936 matrix as the current answer.
The current API is no longer a v2.10 alias.

The historical `rtdsl.v2_9_benchmark_adequacy.*` helpers remain unchanged. The
top-level current API is now an overlay:

```text
rtdl.v3_0.current_benchmark_adequacy.goal4447.v1
```

## What Changed

| App | M51 current reading |
| --- | --- |
| RT-DBSCAN | Adds Goal4445 compact `output_mode="component_signature"` guidance for cluster-size/noise/core summaries and keeps full Python cluster rows explicit. |
| Robot collision | Adds Goal4446 `lowering_mode="numpy_arrays"` guidance for large prepared grouped-segment probes. |
| Barnes-Hut | Marks the row `needs_major_followup`: Goal4442 fused CPU/Numba is faster than current RTDL/OptiX+Numba at tested scales, so Barnes-Hut is not RT-core speedup evidence yet. |
| RTNN | Separates Goal4381 exact float64 aggregate evidence from Goal4443 resident graph-bridge evidence. |
| Triangle counting | Keeps scalar triangle counting primitive-first while adding Goal4444's Numba direct-binary construction fix. |

## Boundary

This is registry cleanup and current guidance alignment. It does not authorize
release action, public speedup wording, whole-app acceleration wording, broad
RT-core wording, paper-reproduction wording, true-zero-copy wording, automatic
partner selection, AMD performance wording, or app-specific native-engine logic.

## Verification

Local checks:

```text
py -m py_compile src/rtdsl/current_benchmark_adequacy.py src/rtdsl/__init__.py
PYTHONPATH=src py -m unittest tests.goal4447_v3_0_m51_current_benchmark_adequacy_refresh_test -v
```
