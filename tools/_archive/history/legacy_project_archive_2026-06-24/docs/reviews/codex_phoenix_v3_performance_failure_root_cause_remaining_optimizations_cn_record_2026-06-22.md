# Codex Record: Phoenix V3 Performance Failure Root Cause and Remaining Optimizations

Date: 2026-06-22
Status: `codex_record_external_review_blocked_not_release`

## Document

```text
docs/reports/phoenix_v3_performance_failure_root_cause_and_remaining_optimizations_cn_2026-06-22.md
```

## Codex Review

The document is accepted as an internal Phoenix V3 technical accounting and
planning record because it:

```text
states the controlling 1.011779x same-hardware V2.14 vs V3 failure;
keeps release/public/broad performance claims blocked;
lists completed optimizations through M3.3/M3.4;
separates material evidence, parity recovery, hygiene cleanup, and row-scoped evidence;
explains why each optimization was technically plausible;
explains why the measured result did not yet become V3-level performance;
lists remaining generic runtime optimizations rather than app-specific patches;
defines success and stop rules before more pod spend.
```

## External Review State

Claude review was attempted once through the known local entrypoint and timed
out without substantive output:

```text
docs/reviews/external_ai_blocked_phoenix_v3_performance_failure_root_cause_remaining_optimizations_cn_2026-06-22.md
```

Therefore this record is not a fresh 2-AI release consensus.

Existing related Claude reviews still constrain the work:

```text
docs/reviews/claude_phoenix_v3_performance_failure_accounting_review_2026-06-22.md
docs/reviews/claude_phoenix_v3_repeated_prepared_session_runner_m3_3_review_2026-06-22.md
docs/reviews/claude_phoenix_v3_rtdbscan_repeated_runner_route_m3_4_review_2026-06-22.md
```

## Boundary

This record does not authorize:

```text
release
public speedup claim
broad V3 faster than V2 claim
full all-app pod rerun
V4 / C ABI / embedding work
```

Phoenix V3 remains:

```text
redo_required
```

## Goal-Level Decision Audit

Decision: accept the new Chinese technical document as an internal record while
recording that the fresh external review attempt was blocked.

1. Was I foolish?
   No. I did not turn a timeout into fake consensus.
2. If yes, what actions made the decision foolish?
   The foolish action would have been to claim 2-AI approval when Claude did not return a verdict.
3. Was there another path that avoids being stuck on a foolish idea?
   Yes. Record the blocked review, preserve the no-release boundary, and keep using already obtained Claude constraints for M3.3/M3.4.
4. Can I now try a different path that truly solves the problem?
   Yes. Continue with focused pod A/B and generic runtime optimization only; do not spend effort on release wording.
