# Handoff: Gemini Review For Goal2371

Please perform an independent read-only review of Goal2371 and write your
review to:

`docs/reviews/goal2372_gemini_review_goal2371_native_prepared_3d_neighbor_2026-05-19.md`

## Scope

Review the new native prepared 3D bounded-neighbor path:

- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/__init__.py`
- `scripts/goal2348_rtnn_v2_2_external_runner.py`
- `tests/goal2371_native_prepared_bounded_neighbor_3d_test.py`
- `docs/reports/goal2371_native_prepared_bounded_neighbor_3d_2026-05-19.md`
- `docs/reports/goal2371_native_prepared_frn3d_pod/*.json`

## Questions

1. Confirm whether the new ABI/API names are app-agnostic and do not introduce
   `rtnn` engine names.
2. Confirm whether the implementation really reuses a native search-side
   uniform-cell structure/device buffers across query runs.
3. Check that the pod evidence supports the report: row counts match Goal2369,
   native prepared mode is `prepared_uniform_cell_compact`, per-run native
   `prepare` is zero, and upload is lower than packed `run-optix`.
4. Check that the interpretation is appropriately bounded: the improvement is
   real, but 262k remains dominated by row download plus host exact refinement.
5. Confirm claim boundaries: no RTNN paper equivalence, no RT-core acceleration
   claim, no broad speedup claim, and no release-readiness claim.

## Expected Verdict

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. Include concise findings and any required follow-up work.
