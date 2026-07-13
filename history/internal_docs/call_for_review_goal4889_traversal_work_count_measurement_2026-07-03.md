# Call For Review: Goal4889 Traversal Work-Count Measurement Gate

Date: 2026-07-03

Requested reviewer: Claude / Antigravity

Requested verdict labels:

- `approve_goal4889_close_with_instrumentation_required_authorize_goal4890_probe`
- `approve_with_amendments`
- `block_goal4889_redo_inventory`

## Context

Goal4888 decomposed the RTDL+Numba RayJoin Section 5.7 hot path and showed that
the main cost is native RT traversal time, not output writing or host transfer.

Claude approved the plan but required AM1:

```text
measure traversal WORK, not just traversal TIME
```

Goal4889 executes that AM1 as a measurement-only gate.

## Files To Review

Goal definition:

```text
history/internal_docs/goal4889_traversal_work_count_measurement_gate_2026-07-03.md
```

Inventory:

```text
history/internal_docs/goal4889_existing_work_count_inventory_2026-07-03.md
```

Source map:

```text
history/internal_docs/goal4889_counter_source_map_2026-07-03.md
```

LSI probe artifact:

```text
history/internal_docs/goal4889_lsi_probe_summary_2026-07-03.json
```

Work-count ledger:

```text
history/internal_docs/goal4889_work_count_ledger_2026-07-03.json
history/internal_docs/goal4889_work_count_ledger_2026-07-03.md
```

Gap and next probe:

```text
history/internal_docs/goal4889_measurement_gap_and_next_probe_2026-07-03.md
```

## Main Finding

Existing evidence proves comparable query/launch counts:

- LSI: 14,430,155 query segments in both RTDL and AuthorPatch.
- PIP map0: 14,788,065 query points in both.
- PIP map1: 992,505 query points in both.
- midpoint PIP: 1,707 and 2,752 query points in both.

But existing evidence does **not** expose candidate/test counts:

- RTDL LSI row route does not report group-candidate events.
- RTDL PIP timing ABI does not report edge/range tests.
- AuthorPatch logs do not report LSI/PIP candidate/test totals.

Therefore Goal4889 closes with:

```text
work_count_unavailable__instrumentation_required
```

## Review Questions

1. Did Goal4889 correctly avoid implementation work and stay measurement-only?
2. Does the evidence justify saying launch/query counts match across RTDL and
   AuthorPatch?
3. Is the interpretation of the LSI probe correct: `raw_candidate_count=0`
   means "not exposed for this route," not "zero candidates"?
4. Is it correct that RTDL PIP currently lacks the required edge/range test
   denominator?
5. Is it correct that existing AuthorPatch logs expose launch sizes/AABB counts
   but not candidate/test totals?
6. Is the decision label
   `work_count_unavailable__instrumentation_required` the right conclusion?
7. Is Goal4890, a temporary measurement-only instrumented build, the right next
   goal before any fusion/compiler/native tuning work?
8. Are the proposed Goal4890 counters sufficient:
   - RTDL LSI group-candidate count;
   - RTDL PIP segment-loop iteration count;
   - AuthorPatch LSI candidate/test count;
   - AuthorPatch PIP candidate/test count?
9. Does the packet correctly avoid claiming that data-flow fusion/compiler work
   is already proven as the next branch?

## Non-Authorization

This review request does not authorize:

- prepared sessions;
- row-buffer ABI;
- Numba partner API implementation;
- native kernel tuning;
- callback APIs;
- RayJoin-specific shortcuts;
- public performance claims.
