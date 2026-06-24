# Handoff: Gemini Review for Goal4032-4036 Partition-Convergence Performance Chain

Date: 2026-06-08

Please perform an independent read-only review of the current RTDL `main` branch, focused on Goals 4032 through 4036.

Write the review to:

`docs/reviews/goal4037_gemini_review_goal4032_4036_partition_convergence_perf_chain_2026-06-08.md`

## Scope

Review these artifacts and source changes:

- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
- `src/rtdsl/__init__.py`
- `tests/goal4027_partition_summary_cupy_preview_test.py`
- `tests/goal4033_partition_device_pair_preview_metadata_refresh_test.py`
- `tests/goal4034_partition_device_pair_preview_timing_test.py`
- `tests/goal4035_partition_component_labels_cupy_preview_test.py`
- `tests/goal4036_partition_component_preview_vs_grouped_stream_timing_test.py`
- `scripts/goal4034_partition_device_pair_preview_timing.py`
- `scripts/goal4036_partition_component_preview_vs_grouped_stream_timing.py`
- `docs/reports/goal4034_partition_device_pair_preview_timing_2026-06-08.md`
- `docs/reports/goal4034_partition_device_pair_preview_timing_pod.json`
- `docs/reports/goal4035_partition_component_labels_cupy_preview_2026-06-08.md`
- `docs/reports/goal4036_partition_component_preview_vs_grouped_stream_timing_2026-06-08.md`
- `docs/reports/goal4036_partition_component_preview_vs_grouped_stream_timing_pod.json`

## Questions

1. Does Goal4032 correctly strengthen the CuPy partition-summary preview with device-bounded pair enumeration while preserving the Goal4019 same-contract validator and Goal4021 component-label oracle boundary?
2. Does Goal4035 correctly add a generic partition-level component-label preview without app-specific engine logic?
3. Does the `cupy_safe_full` safe-full partition union mode remain generic and correctly bounded?
4. Do Goal4034 and Goal4036 timing artifacts support the narrow conclusions stated in the reports?
5. Is the route-selection conclusion honest: partition preview can help warmed one-shot execution, but current grouped-stream remains better for repeated prepared runs?
6. Are all claim boundaries intact: no release, public speedup, broad RT-core, whole-app, hidden dispatch, automatic partner selection, app-specific engine logic, or true-zero-copy authorization?

## Expected Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please lead with findings, then provide the verdict. This review should be independent Gemini evidence and must not count Codex authoring as external consensus.

