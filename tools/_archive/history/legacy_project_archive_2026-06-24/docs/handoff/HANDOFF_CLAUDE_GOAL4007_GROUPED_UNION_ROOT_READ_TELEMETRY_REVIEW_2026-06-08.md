# Handoff: Claude Review Goal4007 Grouped-Union Root-Read Telemetry

Please perform a read-only external review and write the result to:

`docs/reviews/goal4008_claude_review_goal4007_grouped_union_root_read_telemetry_2026-06-08.md`

## Files To Read

- `docs/reports/goal4007_grouped_union_root_read_telemetry_2026-06-08.md`
- `tests/goal4007_grouped_union_root_read_telemetry_test.py`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal3996_grouped_union_extended_telemetry_sweep_pod.py`
- `docs/reports/goal4007_grouped_union_root_read_telemetry_pod/clustered3d_65536.json`
- `docs/reports/goal4007_grouped_union_root_read_telemetry_pod/road3d_65536.json`
- `docs/reports/goal4007_grouped_union_root_read_telemetry_pod/ngsim_dense_65536.json`

## Review Questions

1. Does Goal4007 add only diagnostic root-read telemetry, with no app-shaped ABI and no behavior-changing default?
2. Does the runtime preserve the old 4-counter and 8-counter telemetry contracts while making 10 counters an explicit opt-in?
3. Do the pod artifacts genuinely show source commit `94bf59a4`, ten-counter metadata, and closed claim boundaries?
4. Is the report's interpretation supported: accepted grouped-union route still performs about two root finds per candidate and large parent-link traffic, so the next primitive should reduce candidate/root-read work rather than revive direct-side-effect or microcell defaults?
5. Are there any overclaims, stale release wording, or hidden dispatch/partner claims?

## Expected Format

Use verdict `accept`, `accept-with-boundary`, or `needs-more-evidence`.

Lead with findings by severity. If accepted with boundary, clearly state which findings are release-gate concerns versus current Goal4007 defects.

Please do not edit source files.
