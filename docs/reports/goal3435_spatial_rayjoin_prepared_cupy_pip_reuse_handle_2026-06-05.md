# Goal3435 Spatial RayJoin Prepared CuPy PIP Reuse Handle

**Date:** 2026-06-05  
**Status:** implemented; pod validation pending  
**Scope:** app-facing reusable prepared handle for the Goal3431 PIP route

## Purpose

Goal3431 exposed `prepared_optix_cupy_refined_pip` as a concrete Spatial RayJoin app route. Its first pod artifact was intentionally a cold one-shot CLI run, so preparation dominated the phase timings. Goal3427 already showed the important repeated-query shape: generic RT candidate stream plus prepared CuPy refinement can be much faster once lookup arrays are prepared.

Goal3435 makes that repeated-query shape available to users as a Python API:

```python
prepare_rayjoin_optix_cupy_refined_pip(points, shapes, candidate_max_rows=60000)
```

## What Changed

| File | Operation |
| --- | --- |
| `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` | Added `PreparedRayJoinOptixCupyRefinedPip` and `prepare_rayjoin_optix_cupy_refined_pip(...)`; the one-shot CLI route now delegates through the prepared handle. |
| `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md` | Added a Python API snippet showing repeated calls through the prepared handle. |
| `tests/goal3431_spatial_rayjoin_prepared_cupy_refined_pip_route_test.py` | Expanded regression coverage for the reusable handle, one-shot prepare-paid-in-call metadata, and README guidance. |

## Design

The prepared handle owns:

- the caller's point records;
- the caller's closed-shape records;
- a prepared OptiX point/closed-shape scene;
- a prepared CuPy exact refiner with point, shape, and vertex lookup arrays uploaded once.

Each `run(...)` call produces fresh generic OptiX candidate columns and then refines those columns through the prepared CuPy refiner. The route remains app-layer Python+CuPy over generic RTDL primitives. It does not introduce RayJoin-specific native engine logic.

One-shot CLI calls set:

```json
"prepared_reuse": {
  "enabled": false,
  "prepare_paid_in_call": true,
  "prepare_paid_once": true
}
```

Direct Python handle calls set `enabled: true`, making the repeated-query contract explicit.

## Boundary

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`
- `full_rayjoin_reproduction: False`
- `paper_scale_perf_claim_authorized: False`
- `rtdl_beats_rayjoin_claim_authorized: False`

Goal3435 improves app usability and benchmark repeatability. The warmed performance evidence remains Goal3427 until a dedicated repeated-handle pod artifact is captured.

## Validation Plan

Local:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3431_spatial_rayjoin_prepared_cupy_refined_pip_route_test tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Pod:

```bash
python3 -m unittest tests.goal3431_spatial_rayjoin_prepared_cupy_refined_pip_route_test
python3 - <<'PY'
# repeated-handle smoke to be captured in the final report update
PY
```
