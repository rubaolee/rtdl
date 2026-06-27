# Phoenix V3 AABB Candidate-Stream 32768 M7 Public Surface Closure

Status: bounded closure, not V3 release authorization.

This note records the post-review public-surface closure for exactly one row:

```text
aabb_candidate_stream_all_count_only_float32_32768
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
paper_reproduction_claim_authorized: false
librts_authors_code_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

The allowed wording remains bounded to the native float32-inclusive generic
prepared AABB count-only workload at 32,768 boxes, 32,768 point queries, and
32,768 box queries, warmup=2 and repeat=5, on the RTX 4000 Ada pod:

```text
814.339x query OptiX-over-Embree
132.753x wall OptiX-over-Embree
73.826x elapsed OptiX-over-Embree
```

The row matches an independent chunked NumPy float32 CPU oracle. It does not
match a float64 exact-geometry oracle, so the float32 numeric contract is part
of the claim.

## Review Basis

Claude review:

```text
docs/reviews/claude_phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_review_2026-06-21.md
```

Codex consensus:

```text
docs/reviews/codex_phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_2ai_consensus_2026-06-21.md
```

## Updated Public Surface

The following current-user files now record two exact M7-qualified rows while
keeping V3 release authorization false:

```text
docs/application_catalog.md
docs/backend_maturity.md
docs/performance_model.md
docs/rebuild/v3/README.md
docs/rebuild/v3/v3_current_status_2026-06-20.md
docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md
docs/rebuild/v3/phoenix_v3_m1_m7_compliance_table_2026-06-20.md
tutorials/current/12_aabb_candidate_stream.md
```

## Goal-Level Decision Audit

Decision: close the AABB count-only 32,768 row as the second exact row-scoped
M7-qualified result, then continue Phoenix on the next reusable generic
capability.

1. Was I foolish?

   No. This decision applies the external review after satisfying the P0
   wording condition.

2. If yes, what actions made the decision foolish?

   The foolish action would have been to treat this as a V3 release, a LibRTS
   paper/authors-code reproduction, full spatial-index acceleration, float64
   exact geometry, or a V3-over-V2 headline.

3. Was there another path?

   Yes. I could have kept AABB blocked because the old feasibility packet had
   no CPU reference. That would ignore the later float32 oracle and external
   review.

4. Can I now try a different path that actually solves the problem?

   Yes. Keep this exact-row promotion narrow, keep release and broad claims
   false, and continue Phoenix V3 with the same evidence/review discipline.
