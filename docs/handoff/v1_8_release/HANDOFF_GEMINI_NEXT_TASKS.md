# Handoff: Gemini Next Task

Gemini should stay in independent read-only audit mode.

## Current State

Codex recovered the Goal1707 source-corruption fallout and wrote Goal1708:

- `docs/reports/goal1708_source_recovery_and_semantic_cleanup_2026-05-11.md`
- `tests/goal1708_source_recovery_and_semantic_cleanup_test.py`

The recovery restored the truncated Embree native files, removed stale
`db_copy_dataset_table` / `"DB columnar inputs must not be null"` replay
artifacts, repaired OptiX/Vulkan stale `columns` references in columnar payload
paths, and replaced graph `field_index_count` artifacts with
`edge_index_count`.

## Audit Requirements

1. Confirm the Goal1708 report and test accurately describe the source state.
2. Confirm Embree API/prelude are no longer truncated.
3. Confirm zero hits in `src/native/**` for:
   - `db_copy_dataset_table`
   - `DB columnar inputs must not be null`
   - `field_index_count`
   - the six legacy exported ABI names from Goal1704
4. Confirm strict tracked-family cleanup remains at the documented
   false-positive-only state, and that release readiness still says
   `needs-more-evidence`.
5. Confirm the local `tests.goal903_embree_graph_ray_traversal_test` blocker is
   correctly characterized as a Windows SDK/UCRT/Oracle toolchain failure, not
   a new app-shaped native ABI regression.

## Output

Write the review to:

`docs/reviews/goal1709_gemini_review_goal1708_source_recovery_2026-05-11.md`

Do not edit source files. Do not run pod validation unless explicitly told by
the user.
