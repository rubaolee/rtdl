# External Review Handoff: Goal3734 Shape-Pair Prepared-Left Active Count

Please perform an independent review of Goal3734 and write your review to:

`docs/reviews/goal3736_<your_ai>_review_goal3734_shape_pair_prepared_left_active_count_2026-06-07.md`

Use one of these verdicts only: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Scope

Goal3734 adds a generic prepared-left route for shape-pair active-count queries.
The intended purpose is to remove repeated left-side closed-shape upload from
the RayJoin overlay active-count hot path while keeping native engine vocabulary
generic and app-agnostic.

## Files To Inspect

- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `docs/reports/goal3734_shape_pair_prepared_left_active_count_2026-06-07.md`
- `docs/reports/goal3734_shape_pair_prepared_left_active_count_a5000_overlay_direct_summary.json`
- `docs/reports/goal3734_shape_pair_prepared_left_active_count_a5000_safe_mixed_summary.json`
- `tests/goal3734_shape_pair_prepared_left_active_count_test.py`

## Questions To Answer

1. Does the native implementation remain app-agnostic, or did app/RayJoin logic leak into the engine ABI or implementation?
2. Does the prepared-left route actually reuse left polygon refs, vertices, and bounds from a prepared native handle rather than uploading them in the hot query?
3. Are the Python runtime bindings and lifecycle ownership sound enough for this internal performance route?
4. Does the RayJoin app adoption correctly keep RayJoin interpretation at the Python app layer?
5. Do the A5000 artifacts support the narrow internal conclusion: active-count hot path left upload is removed, overlay active-count improves to about `0.00316s`, and the safe mixed composite reaches about `345.9x` vs all-CuPy on the measured 4096-chain slice?
6. Do the reports/artifacts avoid overclaiming public RayJoin, paper reproduction, release, broad RT-core, true-zero-copy, or whole-app speedup claims?

## Validation Already Run By Codex

Local:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3734_shape_pair_prepared_left_active_count_test `
  tests.goal3442_shape_pair_active_count_device_continuation_test `
  tests.goal3443_spatial_rayjoin_overlay_active_count_device_default_test `
  tests.goal3733_rayjoin_safe_mixed_composite_after_lsi_front_door_test
```

Result: 19 tests passed.

Pod:

- GPU: NVIDIA RTX A5000
- Commit: `c8f3a67c7e770e1e9a7d684ce4521d6b37c9273b`
- `make build-optix` succeeded with `OPTIX_PREFIX=/root/vendor/optix-sdk`.
- Focused pod unit tests passed.
- Direct overlay artifact:
  - `row_count`: `4250`
  - `native_phase_timings.mode`: `active_count_device_continuation_prepared_left`
  - `native_phase_timings.left_prepare`: `0.0`
  - `native_phase_timings.left_upload`: `0.0`
  - `phases_sec.prepared_query_sec`: `0.0031651603057980537`
- Safe mixed composite artifact:
  - PIP `1.000x`
  - LSI `13049.632x`
  - overlay active-count `52.509x`
  - composite sum `345.941x`

## Boundary

This is internal engineering evidence only. It must not authorize a public
release, public RayJoin beat claim, paper-reproduction claim, broad RT-core
claim, true-zero-copy claim, or whole-app speedup claim.
