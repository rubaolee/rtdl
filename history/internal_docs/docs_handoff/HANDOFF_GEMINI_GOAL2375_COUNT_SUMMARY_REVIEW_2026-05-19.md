# Handoff: Gemini Review For Goal2375 Prepared 3D Neighbor Exact Count Summary

Please perform an independent read-only review of Goal2375.

## Files To Read

- `docs/reports/goal2375_prepared_3d_neighbor_exact_count_summary_2026-05-19.md`
- `docs/reports/goal2375_native_prepared_frn3d_count_summary_pod/rtdl_packed_native_prepared_optix_3d_count_summary_65536_r002_k50.json`
- `docs/reports/goal2375_native_prepared_frn3d_count_summary_pod/rtdl_packed_native_prepared_optix_3d_count_summary_262144_r002_k50.json`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal2348_rtnn_v2_2_external_runner.py`
- `tests/goal2375_prepared_3d_neighbor_exact_count_summary_test.py`
- `docs/research/future_version_to_do_list.md`

## Review Questions

1. Does Goal2375 keep the native/runtime surface app-agnostic?
2. Does the new count-summary path correctly avoid row materialization, row
   download, and host exact-refine for `result-mode=count`?
3. Does the report honestly explain that count summary is not a byte-identical
   witness-row replacement, especially because the count and witness contracts
   can differ near boundaries or `k_max` saturation?
4. Does the report avoid RTNN paper-equivalence, RT-core speedup, broad
   runtime speedup, and release-readiness overclaims?
5. Are the tests and pod artifacts sufficient for accepting this as a v2.2
   internal primitive improvement, with boundaries?

## Expected Output

Write your review to:

`docs/reviews/goal2376_gemini_review_goal2375_count_summary_2026-05-19.md`

Use one of these verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.
