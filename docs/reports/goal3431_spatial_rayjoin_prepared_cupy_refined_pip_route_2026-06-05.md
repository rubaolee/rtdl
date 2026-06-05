# Goal3431 Spatial RayJoin Prepared CuPy-Refined PIP Route

**Date:** 2026-06-05  
**Verdict:** implemented; pod artifact pending  
**Scope:** v2.8 benchmark-app adoption of Goal3427 prepared closed-shape refinement

## Purpose

Goal3427 proved that a reusable prepared CuPy closed-shape refiner can reduce repeated PIP refinement overhead by keeping point/shape lookup arrays resident in CuPy device memory. Goal3428 then closed the ordinal chunk-offset guard that Claude found in the native candidate stream.

Goal3431 moves that work from a timing probe into the Spatial RayJoin benchmark app as an explicit user-facing route:

```text
prepared_optix_cupy_refined_pip
```

The route is still app-layer Python+CuPy orchestration over generic RTDL primitives. It is not a native RayJoin implementation.

## What Changed

| File | Operation |
| --- | --- |
| `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` | Added `run_rayjoin_prepared_optix_cupy_refined_pip(...)`, wired it into `--execution-route`, and added `--candidate-max-rows` as an explicit fail-closed capacity knob. |
| `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md` | Documented the route for learners and benchmark users. |
| `src/rtdsl/v2_8_benchmark_runtime_gap.py` | Refreshed the Spatial RayJoin row to cite Goal3424/3427/3428 and record that PIP exact continuation now has an instance-aware candidate stream plus prepared CuPy refiner. |
| `tests/goal3431_spatial_rayjoin_prepared_cupy_refined_pip_route_test.py` | Added regression coverage for the app route, README, v2.8 gap row, report, and optional pod artifact. |

## Route Shape

The new route does:

1. Load the PIP point and closed-shape records through the existing Spatial RayJoin app loader.
2. Prepare the reusable CuPy refiner with the caller's points/shapes.
3. Prepare the generic OptiX point/closed-shape membership scene.
4. Produce generic RT candidate device columns with `point_ordinal` and `shape_ordinal`.
5. Run the prepared CuPy simple-ring refiner on those candidate columns.
6. Return a scalar count by default, with optional host row materialization only when rows are requested.

The native engine sees generic point/closed-shape candidate columns. CuPy performs caller-side simple-ring refinement through the prepared CuPy exact refiner shorthand used in Goal3427. RayJoin/CDB interpretation remains in Python.

## Why This Matters

The old app-facing PIP row route either used prepared native row materialization or forced users to read a standalone Goal3427 timing probe. The new route exposes the v2.8 typed-stream plus partner-continuation shape directly:

```bash
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py \
  --workload pip \
  --execution-route prepared_optix_cupy_refined_pip \
  --result-mode count \
  --candidate-max-rows 60000 \
  --no-rows
```

The expected full public CDB behavior, inherited from Goal3427, is:

- generic RT candidate rows: `47,570`;
- prepared CuPy refined rows: `47,262`;
- host exact row count: `47,262`;
- prepared candidate+refine median in the Goal3427 probe: `0.020430s`;
- host exact median in the Goal3427 probe: `0.084061s`.

Those timing values remain evidence for Goal3427's timing probe, not a new public release claim.

## Boundaries

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`
- `full_rayjoin_reproduction: False`
- `paper_scale_perf_claim_authorized: False`
- `rtdl_beats_rayjoin_claim_authorized: False`

This route improves the benchmark-app reference implementation and makes the v2.8 typed-stream + partner-refiner pattern easier to use. It does not close the broader Spatial RayJoin relation-row gaps: device-resident relation-row output beyond PIP, parity/count grouping over resident rows, and boundary-witness ownership at serious scale remain active v2.8 work.

## Validation

Local validation planned:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3431_spatial_rayjoin_prepared_cupy_refined_pip_route_test tests.goal3105_v2_8_benchmark_runtime_gap_map_test tests.goal3427_prepared_cupy_refiner_timing_test
```

Pod validation is required for the executable CuPy/OptiX route and will be recorded in:

- `docs/reports/goal3431_spatial_rayjoin_prepared_cupy_refined_pip_pod_2026-06-05.json`
- `docs/reports/goal3431_spatial_rayjoin_prepared_cupy_refined_pip_pod_2026-06-05.stdout`
