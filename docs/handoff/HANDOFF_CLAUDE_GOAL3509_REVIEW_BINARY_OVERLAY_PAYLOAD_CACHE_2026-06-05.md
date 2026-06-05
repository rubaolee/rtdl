# Handoff: Claude Review For Goal3509 Binary Overlay Payload Cache

Please perform an independent read-only review of Goal3509 and write the review
to:

`docs/reviews/goal3510_claude_review_goal3509_binary_overlay_payload_cache_2026-06-05.md`

## Context

Goal3509 follows Goal3507. Goal3507 proved a host-side JSON/WKB prepared-payload
cache for repeated public-CDB overlay benchmark runs. Goal3509 keeps the JSON
format as the default, but adds an opt-in binary column cache:

- Prepared payload columns: `.npz`
- Shape-to-component columns: `.npz`
- Geometry WKB byte columns: `.npz`
- Small per-side manifest JSON

The purpose is to reduce cache read overhead and remove bulky JSON arrays/WKB
hex parsing while preserving the same generic prepared simple-polygon component
payload contract.

Commits:

- `d1a9ac19` - `Goal3509 add binary overlay payload cache path`
- `255b66fa` - `Goal3509 record binary overlay payload cache evidence`

## Files To Inspect

- `src/rtdsl/v2_8_overlay_area_prepared_payload.py`
- `src/rtdsl/__init__.py`
- `scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py`
- `tests/goal3509_overlay_area_binary_prepared_payload_cache_test.py`
- `docs/reports/goal3509_overlay_area_binary_prepared_payload_cache_2026-06-05.md`
- `docs/reports/goal3509_overlay_area_binary_prepared_payload_cache_write_pod_2026-06-05.json`
- `docs/reports/goal3509_overlay_area_binary_prepared_payload_cache_read_pod_2026-06-05.json`
- Prior context reports: Goal3502, Goal3504, Goal3505, Goal3507.

## Required Review Questions

Please answer these explicitly:

1. Does Goal3509 preserve the app-agnostic/native-engine boundary? In
   particular, are the new NumPy-column serializers and runner cache helpers
   generic host-side prepared-payload persistence rather than app-specific
   native engine logic?
2. Does the binary read artifact support the reported preparation-stage
   improvement: `1.441s -> 0.171s` versus the Goal3505 8-worker rebuild, and
   `0.355s -> 0.171s` versus Goal3507 JSON read?
3. Does correctness remain unchanged across binary write/read artifacts:
   relation counts, supported/unsupported rows, positive row counts, planned
   triangle pairs, total absolute error, and max relation error?
4. Is JSON correctly left as the default storage format so Goal3507 behavior is
   not silently changed?
5. Are claim boundaries correct and conservative: no release, public speedup,
   broad RT-core speedup, RayJoin reproduction, `rtdl beats RayJoin`, true
   zero-copy, or full overlay claim?
6. What design risks remain before a deeper runtime step, especially `.npz`
   portability, stale-cache validation, cache size, memory-mapped loading,
   device-resident persistence, and cache invalidation?

## Expected Verdict

Use one of the established verdict values:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Do not authorize a release or public speedup claim. If accepted, the expected
shape is likely `accept-with-boundary`: binary cache read is useful repeat-run
evidence, but not true zero-copy or device-resident persistence.
