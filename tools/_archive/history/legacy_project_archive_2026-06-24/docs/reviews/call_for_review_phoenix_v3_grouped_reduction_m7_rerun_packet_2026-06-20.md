# Call For Review: Phoenix V3 Grouped-Reduction M7 Rerun Packet

Date: 2026-06-20

Requested reviewer: Claude

## Scope

Review the fresh grouped-reduction M7 rerun packet before any pod execution.

Primary files:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_rerun_packet_2026-06-20.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_rerun_packet_2026-06-20.json
scripts/v3_phoenix_grouped_reduction_m7_rerun_packet.py
tests/v3_phoenix_grouped_reduction_m7_rerun_packet_test.py
scripts/v3_release_wording_gate.py
scripts/run_test_matrix.py
```

Context:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_feasibility_2026-06-20.md
docs/reviews/claude_phoenix_v3_grouped_reduction_m7_feasibility_review_2026-06-20.md
docs/reviews/codex_phoenix_v3_grouped_reduction_m7_feasibility_2ai_consensus_2026-06-20.md
```

Verification already run by Codex:

```text
py -3 -m unittest tests.v3_phoenix_grouped_reduction_m7_rerun_packet_test
7 tests OK

py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
violations: []

py -3 scripts/run_test_matrix.py --group v3_rebuild
25 modules / 101 tests OK
```

## Review Questions

1. Is this packet safe to use as a pre-pod execution packet?
2. Does it preserve all claim boundaries before execution?
3. Does it correctly standardize the fresh rerun at warmup=3 and forbid
   backfill from old warmup=1/2 evidence?
4. Is the prepared-query public contract draft sufficient for the next run, or
   does it miss any M7-critical field?
5. What P0/P1 fixes are required before Codex writes consensus and considers
   pod execution?

## Required Output

Please save your review to:

```text
docs/reviews/claude_phoenix_v3_grouped_reduction_m7_rerun_packet_review_2026-06-20.md
```

Use verdict:

```text
approve
approve-with-required-fixes
reject
```

List P0 and P1 issues separately.
