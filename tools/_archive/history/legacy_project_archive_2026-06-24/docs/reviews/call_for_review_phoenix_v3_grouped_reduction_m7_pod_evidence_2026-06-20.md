# Call For Review: Phoenix V3 Grouped-Reduction M7 Pod Evidence

Date: 2026-06-20

Requested reviewer: Claude

## Scope

Review the fresh grouped-reduction M7 pod evidence and post-run intake.

Primary files:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_pod_evidence_2026-06-20.md
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m7_20260620/m7_grouped_reduction_post_run_intake.json
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m7_20260620/m7_grouped_reduction_post_run_intake.md
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m7_20260620/m7_grouped_reduction_262144_warmup3.json
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m7_20260620/m7_grouped_reduction_524288_warmup3.json
tests/v3_phoenix_grouped_reduction_m7_pod_evidence_test.py
scripts/v3_phoenix_grouped_reduction_m7_feasibility.py
```

Context:

```text
docs/reviews/codex_phoenix_v3_grouped_reduction_m7_rerun_packet_2ai_consensus_2026-06-20.md
docs/reviews/claude_phoenix_v3_grouped_reduction_m7_rerun_packet_review_2026-06-20.md
```

Verification already run by Codex:

```text
py -3 -m unittest tests.v3_phoenix_grouped_reduction_m7_pod_evidence_test tests.v3_phoenix_grouped_reduction_m7_feasibility_test tests.v3_phoenix_grouped_reduction_m7_rerun_packet_test tests.v3_release_wording_gate_test
20 tests OK

py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
violations: []

py -3 scripts/run_test_matrix.py --group v3_rebuild
26 modules / 106 tests OK
```

## Review Questions

1. Does the report correctly interpret the fresh warmup=3 evidence?
2. Does the post-run intake correctly refuse M7 promotion?
3. Are the hot-query ratios and repeat-aware end-to-end results reported
   honestly?
4. Is it correct that grouped_reduction still needs a public prepared-query
   contract and fresh-result review before any M7 promotion?
5. What P0/P1 fixes are required before Codex writes consensus?

## Required Output

Please save your review to:

```text
docs/reviews/claude_phoenix_v3_grouped_reduction_m7_pod_evidence_review_2026-06-20.md
```

Use verdict:

```text
approve
approve-with-required-fixes
reject
```

List P0 and P1 issues separately.
