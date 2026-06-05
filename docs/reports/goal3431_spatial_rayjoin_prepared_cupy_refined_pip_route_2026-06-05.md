# Goal3431 Spatial RayJoin Prepared CuPy-Refined PIP Route

**Date:** 2026-06-05  
**Verdict:** implemented and pod-validated
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

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3431_spatial_rayjoin_prepared_cupy_refined_pip_route_test tests.goal3105_v2_8_benchmark_runtime_gap_map_test tests.goal3427_prepared_cupy_refiner_timing_test
```

Result:

```text
Ran 13 tests in 0.021s
OK (skipped=1)
```

The skip is the optional CuPy artifact test before pod artifact capture.

Syntax validation used temporary `.pyc` files to avoid the Windows `__pycache__` lock:

```text
syntax ok
```

Pod validation on `root@69.30.85.203:22057`, clean `origin/main` checkout at commit `5e016d19`, rebuilt with `OPTIX_PREFIX=/root/vendor/optix-sdk`:

```bash
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so
python3 examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py \
  --workload pip \
  --execution-route prepared_optix_cupy_refined_pip \
  --result-mode count \
  --candidate-max-rows 60000 \
  --dataset data/rayjoin_public_cdb/br_county.cdb \
  --no-rows
```

Artifact:

- `docs/reports/goal3431_spatial_rayjoin_prepared_cupy_refined_pip_pod_2026-06-05.json`
- `docs/reports/goal3431_spatial_rayjoin_prepared_cupy_refined_pip_pod_2026-06-05.stdout`

Pod result summary:

| Field | Value |
| --- | ---: |
| RT candidate rows | 47,570 |
| Prepared CuPy refined rows | 47,262 |
| Dropped broad-phase candidates | 308 |
| Candidate capacity | 60,000 |
| Candidate required capacity | 47,570 |

Cold single-route phase timings in the CLI artifact:

| Phase | Seconds |
| --- | ---: |
| `prepare_cupy_refiner_sec` | 0.654096 |
| `prepare_static_scene_sec` | 0.675256 |
| `candidate_device_columns_sec` | 0.395151 |
| `prepared_cupy_refine_sec` | 0.068462 |

These are cold route timings from a single app invocation. The warmed repeated-query timing evidence remains Goal3427: candidate stream median `0.018988s`, prepared CuPy refine median `0.001425s`, and candidate+prepared total median `0.020430s`.

Pod test rerun after artifact capture:

```bash
python3 -m unittest \
  tests.goal3431_spatial_rayjoin_prepared_cupy_refined_pip_route_test \
  tests.goal3427_prepared_cupy_refiner_timing_test \
  tests.goal3424_closed_shape_instance_identity_refinement_test
```

Clean `origin/main` pod result at commit `fa17e3e5`:

```text
Ran 14 tests in 0.625s
OK
```

The first pod test attempt exposed a test expectation bug: the candidate metadata does not use a top-level `has_instance_identity_columns` field; the authoritative field is `candidate_columns.runtime.instance_identity_columns.present`. The test was updated to check that contract, and the clean pod rerun passed.
