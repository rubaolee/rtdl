# Call For Review: Phoenix V3 Grouped-Reduction M7 Feasibility

Date: 2026-06-20

Requested reviewer: Claude

## Scope

Review the focused grouped-reduction M7 feasibility packet.

Primary files:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_feasibility_2026-06-20.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_feasibility_2026-06-20.json
scripts/v3_phoenix_grouped_reduction_m7_feasibility.py
tests/v3_phoenix_grouped_reduction_m7_feasibility_test.py
scripts/v3_release_wording_gate.py
scripts/run_test_matrix.py
docs/rebuild/v3/README.md
docs/rebuild/v3/v3_current_status_2026-06-20.md
docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md
```

Source evidence:

```text
docs/rebuild/v3/evidence/phoenix_v3_m4_grouped_continuation_20260620/m28_raydb_grouped_reduction_262144.json
docs/rebuild/v3/evidence/phoenix_v3_raydb_m28_grouped_reduction_20260620/m28_raydb_grouped_reduction_524288.json
docs/reviews/codex_phoenix_v3_raydb_m28_grouped_reduction_2ai_consensus_2026-06-20.md
docs/reviews/codex_phoenix_v3_m7_row_classification_packet_2ai_consensus_2026-06-20.md
```

Verification already run by Codex:

```text
py -3 -m unittest tests.v3_phoenix_grouped_reduction_m7_feasibility_test tests.v3_release_wording_gate_test
7 tests OK

py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
violations: []

py -3 scripts/run_test_matrix.py --group v3_rebuild
24 modules / 93 tests OK
```

## Review Questions

1. Is the repeat-aware amortization math correct for the 262,144-row and
   524,288-row grouped-reduction sources?
2. Does the packet correctly refuse M7 promotion despite hot-query wins?
3. Does it clearly block the false reading "RayDB-style V3 is 158x faster end
   to end"?
4. Are the tests strong enough to guard count break-even, sum cold/setup cost,
   RT-core flag distinction, and release/public claim flags?
5. What P0/P1 fixes are required before Codex writes consensus for this
   feasibility packet?

## Required Output

Please save your review to:

```text
docs/reviews/claude_phoenix_v3_grouped_reduction_m7_feasibility_review_2026-06-20.md
```

Use verdict:

```text
approve
approve-with-required-fixes
reject
```

List P0 and P1 issues separately.
