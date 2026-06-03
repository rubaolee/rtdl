# Goal3157 v2.8 Runtime-Gap RT-DBSCAN Front-Door Refresh

Date: 2026-06-03

Verdict: `accept-with-boundary`

## Purpose

Goal3151 correctly recorded that RT-DBSCAN still used an app-owned component continuation at that time. Goal3155 and Goal3156 changed that: the measured grouped-stream path now has a reusable v2.8 fixed-radius graph component front door, and the RT-DBSCAN benchmark app routes through it while keeping app policy outside the engine.

Goal3157 refreshes the live v2.8 benchmark-runtime gap matrix so it reflects the current state.

## What Changed

| File | Operation |
| --- | --- |
| `src/rtdsl/v2_8_benchmark_runtime_gap.py` | Updated the `rt_dbscan` row to cite the v2.8 fixed-radius graph component front door, current CuPy reference position, remaining typed-producer/conformance work, and Goal3154/3155/3156 evidence. |
| `tests/goal3157_v2_8_runtime_gap_rt_dbscan_front_door_refresh_test.py` | Added regression coverage for the refreshed matrix row and claim boundaries. |

## Current RT-DBSCAN Position

The current best path is:

`fixed-radius/core-summary primitives + v2.8 fixed-radius graph component front door + OptiX/CuPy grouped-stream execution`

What improved:

- users can discover and call the generic fixed-radius graph component continuation;
- the benchmark app no longer calls the lower grouped-stream adapter directly;
- old benchmark mode labels stay compatible;
- the native engine remains app-agnostic.

What remains:

- typed adjacency/grouped-stream producer metadata should become more systematic;
- broader partner conformance is still open, especially a Numba same-contract option;
- this is not a release or public speedup authorization.

## Boundary

Goal3157 is a status refresh, not new performance evidence:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`
- `app_specific_engine_logic_allowed: False`
- `automatic_partner_selection_allowed: False`

The Goal3151 row remains valid history for its timestamp, but it is superseded for current RT-DBSCAN status by Goal3157.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3157_v2_8_runtime_gap_rt_dbscan_front_door_refresh_test tests.goal3105_v2_8_benchmark_runtime_gap_map_test tests.goal3156_rt_dbscan_v2_8_front_door_route_test tests.goal3155_fixed_radius_graph_component_front_door_test
```

Result: 18 tests passed.

Pod validation on `root@69.30.85.131:22063` from clean `origin/main` checkout at commit `04b41bab`:

```bash
python -m unittest \
  tests.goal3157_v2_8_runtime_gap_rt_dbscan_front_door_refresh_test \
  tests.goal3105_v2_8_benchmark_runtime_gap_map_test \
  tests.goal3156_rt_dbscan_v2_8_front_door_route_test \
  tests.goal3155_fixed_radius_graph_component_front_door_test
```

Result: 18 tests passed.
