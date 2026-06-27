# Recorded External Review: Claude Phoenix V3 M35 Focused Gap Ledger

Date: 2026-06-23

Reviewer: Claude

Status: `external_verdict_obtained_claude_accept_m35_gap_ledger_continue_m36_not_release`

Raw capture:

- `docs/reviews/claude_phoenix_v3_m35_focused_gap_ledger_review_2026-06-23.raw.md`
- stderr: `scratch/claude_phoenix_v3_m35_focused_gap_ledger_review_2026-06-23.err.txt`
- runner log: `scratch/claude_phoenix_v3_m35_focused_gap_ledger_review_2026-06-23.log`
- failed attempt preserved:
  `docs/reviews/claude_phoenix_v3_m35_focused_gap_ledger_review_2026-06-23.attempt1.empty.raw.md`
  and `scratch/claude_phoenix_v3_m35_focused_gap_ledger_review_2026-06-23.attempt1.err.txt`

## Verdict

```text
verdict: accept_m35_gap_ledger_continue_m36
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
v4_work_authorized: false
c_abi_work_authorized: false
embedding_work_authorized: false
true_zero_copy_authorized: false
whole_app_speedup_claim_authorized: false
```

## Accepted Classifications

- RTDBSCAN component-signature remains structural-ready but not material. The
  relevant M3.4 runner-vs-legacy geomean is `0.997557675600175x`; the Embree
  comparison is control context, not the incumbent comparison.
- RayJoin point-location remains structural-ready but not material. The
  `0.973754x` total-repeat legacy/runner metric means the runner is slower
  than the incumbent OptiX scalar-count route.
- Grouped reduction is accepted as the right M36 target because it has strong
  row-scoped device-column evidence but lacks a generic runner-callable
  prepared-session core node in the M33/M34 public prepared-session ledger.
- Component union/signature is accepted as the right M37 target because the
  grouped-union pass, not the direct-signature step, remains the likely
  performance source.

## Findings

P0: none.

P1: M35 originally did not acknowledge that the M3.4 RTDBSCAN report had
recommended AABB runner generalization as the immediate next path. Claude
agreed that redirecting to grouped reduction is justified by the later
M30-M34 bundle review, but required the traceability explanation to be written
into M35 before M36 review.

P1 fix applied:

- `docs/reports/phoenix_v3_m35_focused_evidence_gap_ledger_2026-06-23.md`
  now states that M3.4 recommended AABB runner generalization and that the
  M30-M34 bundle review supersedes that sub-milestone direction because grouped
  reduction has stronger existing row-scoped evidence but lacks a
  runner-callable core node.

P2: Claude noted that the Step-1 `0.994858x` citation was not independently
re-read in this review session. The M35 classification still stands because
M3.4 independently supports it.

## Goal-Level Decision Audit

Decision: accept Claude's M35 external verdict, apply the P1 traceability fix,
and proceed toward M36 grouped-reduction core-node work without authorizing
release or all-app POD spend.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   The foolish action would have been ignoring Claude's P1 and letting a future
   reader see conflicting next-path instructions between M3.4 and M35.

3. Was there another path?

   Yes. I could demote M35 to blocked until a new review, but Claude accepted
   the direction and asked for a traceability sentence, not a redesign.

4. Can I now try a different path that actually solves the problem?

   Yes. Continue to M36: promote grouped reduction into a generic
   runner-callable prepared-session core node.

## Non-Authorization

This review and this record authorize no V3 release, no all-app POD spend, no
public speedup claims, no broad V3-over-V2.x claims, no true-zero-copy wording,
no automatic partner selection, no V4 work, no C ABI work, and no embedding
work.
