# Handoff: Claude Review For Goal3507 Overlay Prepared Payload Cache

Please perform an independent read-only review of Goal3507 and write the review
to:

`docs/reviews/goal3508_claude_review_goal3507_overlay_payload_cache_2026-06-05.md`

## Context

Goal3507 follows the Goal3502/3504/3505 public-CDB overlay area chain:

- Goal3502 removed duplicate CPU triangulation in prepared payload construction.
- Goal3504 added an opt-in parallel payload preparation route.
- Goal3505 measured worker counts and found 8 workers best for this pod/dataset.
- Goal3507 adds an opt-in prepared-payload cache so repeated runs can reload
  generic prepared simple-polygon component payload columns instead of rebuilding
  them.

The implementation and evidence are already committed and pushed:

- Code commit: `19b36ccd` (`Goal3507 add reusable overlay payload cache path`)
- Evidence/report commit: `9fc1335d` (`Goal3507 record overlay payload cache evidence`)

## Files To Inspect

- `src/rtdsl/v2_8_overlay_area_prepared_payload.py`
- `src/rtdsl/__init__.py`
- `scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py`
- `tests/goal3507_overlay_area_prepared_payload_cache_test.py`
- `tests/goal3502_overlay_area_single_triangulation_payload_construction_test.py`
- `docs/reports/goal3507_overlay_area_prepared_payload_cache_2026-06-05.md`
- `docs/reports/goal3507_overlay_area_prepared_payload_cache_write_pod_2026-06-05.json`
- `docs/reports/goal3507_overlay_area_prepared_payload_cache_read_pod_2026-06-05.json`
- Prior context reports: Goal3502, Goal3504, Goal3505.

## Required Review Questions

Please answer these explicitly:

1. Does the cache serialize and reload generic prepared payload columns without
   adding app-specific native engine logic?
2. Does read mode genuinely avoid geometry/payload rebuild work, and does the
   artifact evidence support the reported `1.441s -> 0.355s` preparation-stage
   improvement versus the Goal3505 8-worker rebuild?
3. Does correctness stay unchanged between write/read artifacts
   (`total_area_abs_error`, max row error, positive row count, relation counts,
   planned triangle pairs)?
4. Are claim boundaries correct and conservative: no release, public speedup,
   broad RT-core speedup, RayJoin reproduction, `rtdl beats RayJoin`, true
   zero-copy, or full overlay claim?
5. Are there design risks before the next step, especially JSON/WKB cache size,
   stale-cache validation, cache portability, or the gap between host file-cache
   reuse and true device-resident payload persistence?

## Expected Verdict

Use one of the established verdict values:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Do not authorize a release or public speedup claim. If accepted, the expected
shape is likely `accept-with-boundary` because the cache is useful repeat-run
host-side reuse, not true zero-copy or device-resident persistence.
