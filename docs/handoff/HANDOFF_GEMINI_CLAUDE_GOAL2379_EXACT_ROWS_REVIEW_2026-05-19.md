# Handoff: Goal2379 Exact Device Witness Rows Review

Please perform an independent Claude or Gemini review of Goal2379 and write the
review to one of:

- `docs/reviews/goal2380_claude_review_goal2379_exact_rows_2026-05-19.md`
- `docs/reviews/goal2380_gemini_review_goal2379_exact_rows_2026-05-19.md`

## Context

Goal2379 adds an explicit exact device witness-row continuation for prepared 3D
fixed-radius neighbors. It keeps the existing prepared `run_raw(...)` behavior
available and adds `run_exact_raw(...)` / `--result-mode exact-raw`.

The goal is to remove the old host exact-refine stage while still returning
witness rows. It is not a summary contract, not a ranked-K contract, not RTNN
paper equivalence, and not an RT-core claim.

## Files To Inspect

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal2348_rtnn_v2_2_external_runner.py`
- `scripts/goal2379_native_prepared_frn3d_exact_rows_pod_runner.sh`
- `tests/goal2379_prepared_3d_neighbor_exact_rows_test.py`
- `docs/reports/goal2379_prepared_3d_neighbor_exact_rows_2026-05-19.md`
- `docs/reports/goal2379_native_prepared_frn3d_exact_rows_pod/*.json`

## Review Questions

1. Is the new exact-row ABI generic and app-agnostic?
2. Does the Python API keep old `run_raw(...)` behavior and expose the new exact
   path explicitly enough?
3. Do the pod artifacts prove `exact_refine == 0.0` and a speedup over Goal2371
   old prepared rows?
4. Does the report avoid overclaiming ranked-K, RT-core speedup, or RTNN
   paper-equivalence?
5. Are the host/device row struct layout assertions enough for the direct row
   download path?

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`.
The expected conservative verdict is `accept-with-boundary`.
