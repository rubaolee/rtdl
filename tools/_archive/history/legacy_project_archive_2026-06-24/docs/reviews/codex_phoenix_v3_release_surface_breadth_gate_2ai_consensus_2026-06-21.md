# Codex Consensus: Phoenix V3 Release Surface Breadth Gate

Date: 2026-06-21
Status: `claude_codex_consensus_release_surface_breadth_gate_complete_not_release`

## Verdict

`approve-with-amendments-complete`

The Phoenix V3 release-surface breadth gate is accepted as the current
machine-readable form of the `eleven_row_surface_still_too_narrow_for_major_release`
blocker. It does not authorize release, public speedup wording, broad
V3-over-V2 wording, or package/install wording.

## External Review

Claude review:

- `docs/reviews/claude_phoenix_v3_release_surface_breadth_gate_review_2026-06-21.md`
- Verdict: `approve-with-amendments`
- P0 findings: none.

Claude P1 fixes are complete:

- P1-1 fixed: `missing_capability_future_work_map` now machine-maps
  `aggregate_frontier -> barnes_hut_vector_accumulation_frontier_shape -> vector_accumulation`
  and `point_location_topology_stream -> spatial_rayjoin_topology_stream_author_gap -> point_location_topology_stream`.
- P1-2 fixed: `apps_with_m7_rows` now reads both `m7_row_id` and `m7_row_ids`, accounts for all 8 app-boundary M7 rows, and records zero unattributed app-boundary rows.
- P1-3 fixed: the aggregate release-readiness gate now promotes
  `missing_aggregate_frontier_m7_capability_family` and
  `missing_point_location_topology_stream_m7_capability_family` into top-level
  `blocking_reasons`.

## Current Facts

- Current M7 row-scoped surface: 11 rows.
- Current M7 capability-family coverage: 7 / 9.
- Missing M7 capability families:
  - `aggregate_frontier`
  - `point_location_topology_stream`
- App-boundary M7 rows attributed to named apps: 8 / 8.
- Active generic-engine queue: empty.
- Existing evidence promotable now: false.
- Release authorization: false.

## Validation

```text
py -3 -m unittest tests.v3_phoenix_release_surface_breadth_gate_test tests.v3_release_wording_gate_test tests.v3_phoenix_release_readiness_gate_test
Result: 8 tests OK

py -3 scripts/run_test_matrix.py --group v3_rebuild
Result: 92 modules / 441 tests OK
```

## Decision Self-Audit

- Decision: Accept the surface-breadth gate as a governance artifact while keeping Phoenix V3 release blocked.
- Was I foolish? No. The work makes the release blocker more exact and harder to misread.
- Foolish actions: The foolish action would be to treat this stronger gate as a release approval, or to hide the two missing capability families inside secondary evidence.
- Other path: Leave Claude's P1 findings as known issues. That would preserve ambiguity for the next AI.
- Different path now: Use the fixed gate as the current source of truth for V3 breadth, and continue only through new generic M7 evidence or an explicit product-scope decision.
