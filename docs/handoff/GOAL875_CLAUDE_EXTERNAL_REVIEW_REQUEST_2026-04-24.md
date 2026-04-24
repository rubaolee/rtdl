# Goal875 Claude External Review Request

Please review Goal875 in `/Users/rl2025/rtdl_python_only`.

Files:

- `src/rtdsl/app_support_matrix.py`
- `docs/app_engine_support_matrix.md`
- `docs/features/segment_polygon_anyhit_rows/README.md`
- `docs/tutorials/segment_polygon_workloads.md`
- `tests/goal858_segment_polygon_docs_optix_boundary_test.py`
- `docs/reports/goal875_segment_polygon_anyhit_status_refresh_2026-04-24.md`
- `docs/reports/goal875_codex_review_2026-04-24.md`

Question:

Do the current docs and matrices correctly state the new status of
`segment_polygon_anyhit_rows`: internal native bounded OptiX pair-row emitter
exists, but public rows path remains host-indexed and no RTX claim is allowed
until Goal873 strict RTX validation passes?

Return a concise markdown verdict: `ACCEPT`, `ACCEPT_WITH_CAVEATS`, or `BLOCK`,
with concrete reasons.
