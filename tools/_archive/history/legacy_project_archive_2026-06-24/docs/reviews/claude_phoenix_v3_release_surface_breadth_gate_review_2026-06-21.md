# Claude Review: Phoenix V3 Release Surface Breadth Gate

Reviewer: Claude Code via local `C:\Users\Lestat\.local\bin\claude.exe`
Date: 2026-06-21

```text
Verdict: `approve-with-amendments`

P0 Findings
- None.

P1 Findings
- P1-1  Capability-name mismatch is not machine-checkable.
  The M7 packet records the Barnes-Hut gap as planned capability
  `aggregate_frontier`; the future-research work-queue item for the same gap
  carries `generic_capability: "vector_accumulation"`. The breadth gate's
  `missing_m7_capability_families` list contains `aggregate_frontier`, but
  `evidence.future_research_capabilities` contains `vector_accumulation` - with
  no machine assertion linking them. The only bridge is the prose
  `capability_scope_note`. The test (breadth_gate_test.py:55) explicitly checks
  both names as separate set members, which means a downstream agent attempting
  to reconcile the missing-capability name with its future-work record by
  equality will silently fail. If the packet's planned capability name is later
  corrected to `vector_accumulation`, the current check
  `missing_packet_capabilities_are_expected_gaps` will break; if it is changed
  in the queue instead, the link disappears entirely.

- P1-2  `apps_with_m7_rows` in the breadth gate JSON attributes only 3 rows
  (under `raydb_style`) while `app_boundary_m7_rows` claims 8.  The 5 rows
  covering `aabb_candidate_stream`, `component_union`, `prepared_graph_chunk`,
  `threshold_summary`, and `collision_flag_stream` are not attributed to a named
  app in the breadth gate's evidence. `_app_m7_rows` reads
  `app.get("m7_row_ids", [])` per app; if those rows are counted at the
  top-level `phoenix_m7_qualified_release_rows` field of the app-classification
  file rather than inside per-app `m7_row_ids` arrays, the breadth gate evidence
  is structurally incomplete. No test validates that `apps_with_m7_rows` covers
  all 8 claimed app-boundary rows.

- P1-3  The readiness gate's top-level `blocking_reasons` list uses only the
  umbrella label `eleven_row_surface_still_too_narrow_for_major_release`; it
  does not surface the specific capability-gap identifiers
  (`missing_aggregate_frontier_m7_capability_family`,
  `missing_point_location_topology_stream_m7_capability_family`) that the
  breadth gate generates. A consumer parsing only the readiness gate's
  `blocking_reasons` cannot learn the specific gaps without also reading
  `evidence.release_surface_breadth_blocking_reasons`. This is an evidence
  depth issue, not a safety issue, but it will cause confusion if the readiness
  gate is the only artifact a downstream reviewer consults.

Required Fixes
- Fix P1-1: Add a machine-readable field in the breadth gate payload that maps
  each missing planned capability family to its canonical future-research ID and
  the queue's capability name. Assert this mapping in the test so a rename in
  either artifact breaks the check immediately.
- Fix P1-2: Either update `_app_m7_rows` to attribute all 8 app-boundary rows to
  named apps, or add a separate `unattributed_app_boundary_m7_rows` count field
  with an assertion that
  `sum(len(rows) for rows in apps_with_m7_rows.values()) + unattributed == app_boundary_m7_rows`.
  Add a test assertion that `apps_with_m7_rows` accounts for all 8 rows.
- Fix P1-3 (optional but recommended): Either promote the two specific
  missing-family reasons into the readiness gate's top-level `blocking_reasons`,
  or add a test assertion that the readiness gate's evidence correctly carries
  both capability-gap names, making the omission from the summary an explicit
  documented choice rather than an oversight.

Notes
- All three authorization flags (`release_authorized`, `public_speedup_claim_authorized`,
  `broad_v3_faster_than_v2_claim_authorized`) are hardcoded `False` in every
  code path across all three scripts. This is the correct pattern and provides
  an unconditional safety property.
- The 21 breadth-gate structural checks are correctly grounded: row count,
  capability coverage, missing family names, queue status, and promotability are
  all read from the same JSON sources the M7 packet and app-classification files
  use authoritatively. There is no invented evidence.
- The readiness gate's 8 new breadth-gate integration checks (lines 490-521 of
  v3_phoenix_release_readiness_gate.py) use exact value assertions, not
  existence checks. This is the right pattern for consuming a sub-gate.
- The aggregate consensus file correctly contains
  `aggregate_release_readiness_consensus_blocks_release` (the literal string the
  breadth gate substring-searches for), so the breadth gate's
  `aggregate_release_consensus_blocks_release` check is correctly grounded in
  the consensus document.
- Return code conventions are correct and consistent: breadth gate exits 0 on
  `surface_breadth_blocked_not_release`, exits 2 on `fail`; readiness gate exits
  0 on `blocked_not_release`, 1 with `--strict-release`, 2 on `fail`. These are
  safe and unambiguous.
```
