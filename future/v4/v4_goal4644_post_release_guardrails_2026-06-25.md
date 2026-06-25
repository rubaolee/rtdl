# V4 Goal4644 Post-Release Guardrails And Debt Ledger

Status: `v4_0_0_post_release_guardrails_active`

Decision:

`activate_post_release_guardrails_and_debt_ledger`

## Purpose

Goal4644 closes the immediate V4.0.0 publication chain by making the release
guardrails explicit and machine-checkable after publication. The release is
already authorized by Goal4642 and published by Goal4643; this goal prevents
that publication from drifting into broader claims.

Goal4644 does not reopen V4.0 scope. New partner support, Tier-3 callbacks,
CuPy performance, C ABI/embedding, non-Python host support, or additional
operator families must be V4.x work unless a later reviewed goal explicitly
changes that scope.

## Current Release State

- Release label:
  `RTDL v4.0.0 bounded operator release: 8 generic RT-core operators faster than brute-force partner/CPU baselines`
- Publication commit:
  `c58642326f57f6326274b448caa8d75b3c7ef9de`
- Measured V4.0 operator surfaces: `8`
- Candidate V4.0 release surfaces: `0`
- Deferred/excluded V4.0 benchmark families: `2`

## Guardrails

The following claims remain forbidden after publication:

- broad V4 speedup;
- whole-application speedup;
- all-benchmark speedup;
- public true-zero-copy;
- Tier-3 callback support;
- raw OptiX callback support;
- CuPy performance;
- C ABI / embedding / non-Python host;
- app-specific native kernels;
- Barnes-Hut covered by V4.0;
- Spatial RayJoin covered by V4.0;
- LibRTS paper reproduction.

The important distinction is:

- allowed: bounded V4.0.0 release wording for the documented measured generic
  RT-core operator surfaces beating stated brute-force partner/CPU baselines
  on the frozen Goal4639 scorecard;
- forbidden: expanding that wording into whole-application, all-benchmark,
  near-handwritten-OptiX, callback, partner, or host-language claims.

## Required Records

Machine-readable release and guardrail records:

- `src/rtdsl/v4_release_decision.py`
- `src/rtdsl/v4_goal4643_publication_decision.py`
- `src/rtdsl/v4_goal4644_post_release_guardrails.py`

Human-readable records:

- `future/v4/v4_goal4642_final_3ai_release_authorization_packet_2026-06-25.md`
- `future/v4/v4_goal4643_publication_decision_2026-06-25.md`
- `future/v4/v4_goal4644_post_release_guardrails_2026-06-25.md`

Public front-door docs:

- `README.md`
- `docs/current_v4_status.md`
- `docs/learn/performance_wording.md`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`
- `future/v4/v4_0_scope_gate.md`

## Review Cadence

Owner rule preserved:

- every 6 hours of continued V4 work: ask Claude or Antigravity for external
  review, or record review debt if the reviewer/tool is unavailable;
- every 24 hours of continued V4 work: obtain or request 3-AI consensus, or
  record explicit review debt if an AI seat is unavailable.

Current post-release review status:

- Goal4642 final release authorization already has three independent seats:
  Antigravity, independent Codex, and main Codex release-owner audit.
- Goal4644 external review has been completed by Claude:
  `future/v4/reviews/claude_v4_goal4644_post_release_guardrails_review_2026-06-25.md`
- Claude verdict:
  `accept_goal4644_post_release_guardrails`
- Antigravity review is optional debt for Goal4644 because Claude completed the
  current 6-hour external review seat.
- The next Antigravity or Claude review is due after another 6 hours of
  continued V4 work or at the next major decision.

This optional debt does not weaken the release label. It only records the next
review maintenance obligation.

## Tests

Goal4644 is covered by:

- `tests/v4_goal4644_post_release_guardrails_test.py`
- `tests/v4_goal4643_publication_decision_test.py`
- `tests/v4_frontdoor_test.py`
- `tests/v4_scope_gate_test.py`
- `tests/v4_catalog_regression_gate_test.py`

The tests assert:

- deferred families remain excluded from V4.0 claims;
- candidates are not counted as measured release surfaces;
- public docs retain caveats;
- forbidden claims remain machine-visible;
- Goal4644 does not reopen V4.0 scope.

## Goal-Level Decision Audit

Was I stupid?

No. This goal is a guardrail after publication, not a new release expansion.

If yes, what actions would have made the decision stupid?

It would be stupid to use a post-release guardrail goal to smuggle V4.x features
into V4.0, to erase review debt, or to soften the forbidden-claims list after
publication.

Was there another possibility that avoids getting stuck on a bad path?

Yes. The alternative is to keep V4.0 fixed and require every new capability to
enter through a new reviewed V4.x goal.

Can I start a different path that actually solves the problem?

Yes. The real path is to keep V4.0 bounded and use new goals for future
operator coverage, partner validation, Tier-3 callback work, or embedding.

## Non-Authorization

Goal4644 does not authorize broad speedup claims, whole-application speedup
claims, all-benchmark speedup claims, public true-zero-copy claims, Tier-3
callback support, raw OptiX callback API support, CuPy performance claims, C ABI,
embedding, non-Python host bindings, app-specific native kernels, Barnes-Hut
coverage, Spatial RayJoin coverage, or LibRTS paper reproduction.
