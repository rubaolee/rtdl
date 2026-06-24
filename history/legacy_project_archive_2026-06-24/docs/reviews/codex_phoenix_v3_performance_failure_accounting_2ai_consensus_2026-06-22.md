# Codex Consensus: Phoenix V3 Performance Failure Accounting

Date: 2026-06-22
Status: `2ai_consensus_complete_accounting_approved_with_edits_applied`

## Inputs

- Accounting document:
  `docs/reports/phoenix_v3_performance_failure_optimization_accounting_2026-06-22.md`
- Call for review:
  `docs/reviews/call_for_review_phoenix_v3_performance_failure_accounting_2026-06-22.md`
- Claude review:
  `docs/reviews/claude_phoenix_v3_performance_failure_accounting_review_2026-06-22.md`

## External Verdict

Claude's verdict:

```text
approve_with_required_edits
```

Claude agreed with the core accounting:

- Phoenix V3 currently lacks release-level performance proof.
- The 1.012x same-hardware all-app geomean blocks release.
- Regression repair, row-scoped wins, hot-query wins, and runner parity
  recovery must not be promoted into broad V3 success.
- The remaining responsible work must stay in language/runtime mechanisms, not
  benchmark-app development.

Claude required edits before the document could serve as handoff accounting.

## Edits Applied

Required edit 1: add explicit classification per optimization.

Applied:

- Section 2 now has a `Category` column.
- Labels include `regression_repair`, `parity_recovery`,
  `hot_query_amortized_row_scoped`, `runner_parity_recovery`,
  `row_scoped_continuation`, and `productized_path_win_row_scoped`.

Required edit 2: replace ambiguous "focused estimate" wording.

Applied:

- Barnes-Hut now says the focused packet recovered specific serious-run losses:
  `0.622x -> 0.999x`, `0.591x -> 1.038x`, and `0.961x -> 0.990x`.
- The `1.009x` Barnes-Hut app number is explicitly called a post-hoc
  projection if focused rows supersede old serious rows, not a new full
  all-app run.

Required edit 3: quantify RTNN hot-query and cold/wall results.

Applied:

- RTNN repeat50 now records all three required numbers together:
  `7.889x` hot-query, `1.315x` cold-plus-query, and `3.761x` runner-wall.
- RTNN symbol-cache focused run is separately recorded as `1.001x` geomean
  patched V3 vs V2.14 across 12 stress rows.

Required edit 4: clarify AABB and RTNN app-vs-runtime boundary.

Applied:

- AABB generalization now distinguishes the generic runtime artifact from
  Contact Manifold / LibRTS measurement probes.
- RTNN amortization now distinguishes the generic amortized prepared-session
  artifact from the RTNN measurement probe.

Required edit 5: add failure-mode conditions.

Applied:

- Each Section 6 item now has an explicit failure mode saying when to stop
  treating that path as material V3 speed evidence.

Required edit 6: mention CUDA launch/stream/allocator scope.

Applied:

- Section 2 now states that CUDA launch-configuration tuning, stream
  concurrency, and allocator-policy work are not credited as completed Phoenix
  V3 performance optimizations in the current handoff set.

## Codex Consensus

Codex accepts Claude's review and confirms that the required edits have been
applied.

The accounting document is now suitable as the Phoenix V3 technical accounting
handoff for:

- what optimization work has been done;
- which work failed to deliver release-level performance;
- why the original expectations were technically plausible;
- why actual evidence did not clear the V3 bar;
- which remaining optimization paths are generic runtime work; and
- where to stop if those paths asymptote to parity.

## Non-Authorization

This consensus does not authorize:

- Phoenix V3 release;
- public performance wording;
- broad V3 faster than V2.x claims;
- true zero-copy claims;
- automatic backend/partner selection;
- V4, C ABI, embedding, SDK, or external host interop work.

Phoenix V3 remains:

```text
status: redo_required
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

## Goal-Level Decision Audit

Decision: accept the two-AI accounting consensus and use the edited accounting
document as the current Phoenix V3 performance-failure handoff.

1. Was I foolish?
   No for this decision.
2. If yes, what actions made the decision foolish?
   The foolish action would have been to leave ambiguous categories, unnumbered
   RTNN hot-query claims, or "estimate" wording in a document meant to explain
   why V3 has no release-level performance.
3. Was there another path?
   Yes. I could have skipped external review and handed the document directly
   to the user, but that would violate the Phoenix discipline for goal-level
   decisions.
4. Can I now try a different path that truly solves the problem?
   Yes. The next path is to execute only the remaining generic runtime
   optimizations with explicit failure modes, not more app-shaped patching or
   release language.
