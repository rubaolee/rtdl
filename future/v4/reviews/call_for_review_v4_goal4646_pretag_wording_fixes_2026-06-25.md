# Call For Review: V4 Goal4646 Pre-Tag Wording Fixes

Requested reviewers: Claude and Antigravity.

This is a tag-gating wording review, not a new performance authorization.

## Background

Claude's V4.0.0 release review accepted the release as a bounded operator
release but blocked the public tag until three wording fixes were completed:

1. qualify the label as faster than brute-force partner/CPU baselines on eight
   generic operators;
2. report the ratio distribution, not the raw 5.185x geomean as headline;
3. state denominator and scale for every representative ratio.

Primary source:

- `docs/reviews/claude_v4_0_0_release_review_2026-06-25.md`
- `future/v4/v4_goal4646_pretag_mandatory_wording_fixes_2026-06-25.md`

Completion record:

- `future/v4/v4_goal4646_pretag_wording_fixes_completion_2026-06-25.md`

## Files To Inspect

- `README.md`
- `docs/current_v4_status.md`
- `docs/learn/performance_wording.md`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`
- `future/v4/v4_goal4639_serious_release_scorecard_pod_gate_decision_2026-06-25.md`
- `future/v4/v4_goal4642_final_3ai_release_authorization_packet_2026-06-25.md`
- `future/v4/v4_goal4643_publication_decision_2026-06-25.md`
- `future/v4/v4_goal4644_post_release_guardrails_2026-06-25.md`
- `future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/summary.md`
- `scripts/v4_catalog_regression_gate.py`
- `src/rtdsl/v4.py`
- `src/rtdsl/v4_release_decision.py`
- `src/rtdsl/v4_scope.py`
- `src/rtdsl/v4_goal4639_release_scorecard_decision.py`
- `tests/v4_goal4646_pretag_wording_fixes_test.py`

## Verification To Check

Recorded as passing:

- targeted wording/release group: `39 tests OK`;
- full V4 group: `185 tests OK`;
- catalog dry-run: `status: passed`, new bounded label printed;
- quickstart: `status: ok`, new bounded label printed;
- public-surface old-label grep: no matches.

## Questions

1. Are Fix 1, Fix 2, and Fix 3 genuinely completed?
2. Does current public wording avoid the old unqualified high-performance label?
3. Is the raw 5.185x geomean demoted from public headline to internal scorecard
   math?
4. Are point-nearest and AABB clearly labeled as scale-dependent
   algorithmic-complexity wins, not kernel-quality or near-OptiX wins?
5. Does every representative ratio have a baseline/denominator and scale?
6. Did the changes preserve V4.0 scope boundaries and forbidden claims?
7. Is the public tag unblocked by wording, or are amendments still required?

## Required Verdict

Choose one:

- `accept_goal4646_wording_fixes_tag_unblocked`
- `accept_with_required_amendments_before_tag`
- `reject_goal4646_old_overclaim_remains`
- `blocked_unable_to_review`

## Non-Authorization

This review may only unblock the wording/tag gate. It must not authorize broad
V4 speedup, whole-application speedup, all-benchmark speedup,
near-handwritten-OptiX performance, public true-zero-copy, Tier-3 callback
support, raw OptiX callback support, CuPy performance, C ABI, embedding,
non-Python host bindings, app-specific native kernels, Barnes-Hut coverage,
Spatial RayJoin coverage, or LibRTS paper reproduction.

## Requested Output

Write a complete review with:

- one verdict label;
- findings by severity;
- answers to all seven questions;
- tag-blocker disposition;
- explicit non-authorization block.
