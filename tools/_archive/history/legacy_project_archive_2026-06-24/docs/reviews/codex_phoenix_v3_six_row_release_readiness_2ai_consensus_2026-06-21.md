# Codex Consensus - Phoenix V3 Six-Row Release Readiness

Status: Claude + Codex consensus complete.

Date: 2026-06-21.

## Inputs

Claude review request:

```text
docs/reviews/claude_request_phoenix_v3_six_row_release_readiness_review_2026-06-21.md
```

Claude review:

```text
docs/reviews/claude_phoenix_v3_six_row_release_readiness_review_2026-06-21.md
```

Current classification packet:

```text
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.json
```

## Consensus Verdict

Codex accepts Claude's main verdict:

```text
bounded_six_row_exact_claim_surface_only
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
Phoenix M7-qualified release rows: 6
```

V3 is not ready to be called a responsible major release. The current Phoenix
state is a strict, evidence-backed six-row exact-claim surface.

## Clarifications

Claude flagged Robot Collision P1 amendments as not verified. That was caused
by the global review request omitting the final Robot Collision packet from the
review set. Codex verifies that the amendments are applied and gate-protected:

```text
docs/rebuild/v3/phoenix_v3_robot_collision_flag_stream_no_probe_paired_rtx_evidence_2026-06-21.md
static obstacle triangles | 4,096
The tail and window speedups measure the prepared query execution phase
the wrapper speedup is the conservative process-level bound
current_packet_external_review_status: claude_approved_with_p1_amendments_resolved
```

The wording gate and tutorial tests also require these exact disclosures.

Claude's P2 performance-model inconsistency was valid and is now fixed:

```text
docs/performance_model.md
```

The page now says the M7 wording boundary is true only for six exact rows.

## User-Facing Answer

1. We are building a V3 engine surface, but only six reusable generic rows are
   currently M7-qualified. This is not a collection of app-specific native
   engines, and it is not a broad language-generation win yet.
2. There are meaningful speedups in exact rows, including grouped reduction,
   AABB, Triangle, and Robot Collision prepared flag-stream work. The broad
   same-row V3-vs-V2.14 geomean remains 1.012x, so a broad speedup claim is
   forbidden.
3. V3 is not major-release-ready. It is a bounded six-row exact-claim surface.
4. The current Phoenix work is materially necessary because it prevented a
   false release and produced a clean, reviewable truth surface. It is not
   enough by itself to finish V3.
5. Next work must be installer/reproducibility, external review cleanup,
   second-machine performance strategy, comprehensive wording scanner, and a
   clear V3 value proposition.

## Goal-Level Decision Audit

Decision: do not declare V3 release-ready; record the current state as a
bounded six-row exact-claim surface and move the next work from row promotion to
release infrastructure and product-scope closure.

1. Was I foolish?

   No. This decision follows the evidence and the external Claude review
   instead of trying to turn six rows into a major-release claim.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish actions would be publishing a broad V3-over-V2
   claim from a 1.012x geomean, calling row-scoped evidence whole-app evidence,
   or treating current docs/tests as a substitute for installability.

3. Was there another path?

   Yes. Continue promoting more rows from current evidence. Claude and Codex
   both reject that as the next priority because the current reopen queue is
   empty and release blockers are now infrastructure/review/product blockers.

4. Can I now try a different path that actually solves the problem?

   Yes. The next path is installer/reproducibility first, then external review
   cleanup, second-machine performance strategy, a stronger wording scanner,
   and final V3 product-scope decision.
