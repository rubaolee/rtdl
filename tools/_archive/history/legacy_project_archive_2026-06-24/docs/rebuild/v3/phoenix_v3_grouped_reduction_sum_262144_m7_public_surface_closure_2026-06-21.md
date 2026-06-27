# Phoenix V3 Grouped-Reduction Sum 262144 M7 Public Surface Closure

Status: bounded closure, not V3 release authorization.

This note records the post-review public-surface closure for exactly one row:

```text
grouped_reduction_sum_scalar_broadcast_repeat100_262144
```

## Decision

Promote only this row as M7-qualified row-scoped public wording:

```text
row_scoped_public_speedup_claim_authorized: true
m7_promotion_authorized: true
m7_qualified_release_rows: 1
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

The allowed wording remains bounded to the fixed-schema prepared grouped-sum
workload at 262,144 rows / 1,024 groups, warmup=3, actual repeat=100, on the
RTX 4000 Ada pod:

```text
200.353x actual repeat100 prepared-loop speedup
27.917x cold-plus-loop speedup
```

The 524,288-row grouped-sum row, count rows, RayDB whole-app claims, and broad
V3-over-V2 claims remain blocked.

## Review Basis

Claude review:

```text
docs/reviews/claude_phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_review_2026-06-21.md
```

Codex consensus:

```text
docs/reviews/codex_phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2ai_consensus_2026-06-21.md
```

Source provenance condition:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_scalar_broadcast_repeat100_20260620/source_manifest.sha256
```

The pod artifact has no usable git HEAD, so the source manifest is the source
traceability record for this promotion.

## Updated Public Surface

The following current-user files now record one exact M7-qualified row while
keeping V3 release authorization false:

```text
docs/application_catalog.md
docs/backend_maturity.md
docs/performance_model.md
docs/rebuild/v3/README.md
docs/rebuild/v3/v3_current_status_2026-06-20.md
docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md
docs/rebuild/v3/phoenix_v3_m1_m7_compliance_table_2026-06-20.md
tutorials/current/07_grouped_sum_prepared_query.md
```

## Verification

Focused tests:

```text
py -3 -m unittest tests.v3_phoenix_grouped_reduction_sum_262144_m7_final_review_packet_test tests.v3_phoenix_m7_row_classification_packet_test tests.v3_phoenix_grouped_reduction_sum_m7_candidate_wording_test tests.v3_public_docs_rebuild_surface_test tests.v3_rebuild_tutorial_surface_test tests.v3_release_wording_gate_test
```

Result:

```text
43 tests OK
```

Wording gate:

```text
py -3 scripts\v3_release_wording_gate.py --pretty
```

Result:

```text
status: pass
missing_required_strings: []
violations: []
```

V3 rebuild matrix:

```text
py -3 scripts\run_test_matrix.py --group v3_rebuild
```

Result:

```text
42 modules
199 tests OK
```

## Goal-Level Decision Audit

Decision: close the grouped-reduction 262,144 sum row as the first exact
row-scoped M7-qualified result, then continue Phoenix on the next reusable
generic capability.

1. Was I foolish?

   No. This decision applies the external review instead of self-promoting from
   local evidence.

2. If yes, what actions made the decision foolish?

   The foolish action would have been to turn one row into a broad V3 release,
   RayDB whole-app speedup, 524,288-row claim, or V3-over-V2 headline.

3. Was there another path?

   Yes. I could have kept the row blocked because an earlier review attempt
   failed. That would ignore the later successful Claude review and leave the
   public surface stale.

4. Can I now try a different path that actually solves the problem?

   Yes. Keep this exact-row promotion narrow, keep release false, and move to
   the next generic Phoenix candidate with the same evidence/review discipline.
