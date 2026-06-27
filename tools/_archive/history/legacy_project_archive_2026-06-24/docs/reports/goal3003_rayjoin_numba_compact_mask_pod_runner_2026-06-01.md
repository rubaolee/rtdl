# Goal3003: RayJoin Numba Compact Mask Pod Runner

## Purpose

Goal3003 prepares CUDA runtime evidence for Goal3002's RayJoin-style v2.6 Numba compact-mask app wiring.

The runner executes all three RayJoin benchmark workloads:

- `pip`
- `lsi`
- `overlay_seed`

Each workload receives deterministic `candidate_row_ids:int64` and `keep_mask:bool` Numba CUDA arrays. The app wrapper calls the generic `compact_mask_i64` primitive, then the runner compares selected candidate ids and original indices against a CPU oracle.

## Runner

`scripts/goal3003_rayjoin_numba_compact_mask_pod_runner.py`

## Boundary

Goal3003 is app-level continuation conformance, not a RayJoin paper reproduction and not a performance claim. It must not authorize v2.6 release, public speedup wording, Numba speedup wording, RT-core speedup wording, whole-app speedup wording, true-zero-copy wording, or `RTDL beats RayJoin` wording.
