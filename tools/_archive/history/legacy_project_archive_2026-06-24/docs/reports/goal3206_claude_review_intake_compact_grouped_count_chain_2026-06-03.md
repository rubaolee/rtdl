# Goal3206: Claude Review Intake for Compact Grouped-Count Chain

Date: 2026-06-03

## Purpose

Goal3206 records the intake of Claude's independent Goal3202 review of the
compact grouped-count / RayJoin chain.

Review file:

- `docs/reviews/goal3202_claude_review_compact_grouped_count_rayjoin_chain_2026-06-03.md`

Claude's verdict was `accept-with-boundary`. No medium-severity correctness,
ABI, or claim-boundary issue was found.

## Findings And Actions

| Finding | Status | Action |
| --- | --- | --- |
| L1: Pair-column grouped-count wrappers hardcode `left_id` | Closed | Runtime docstrings now explicitly state these wrappers count by the pair-column `left_id` axis. |
| L2: Dense grouped-count output lacks explicit key semantics | Closed | Dense metadata now records `group_key_semantics: dense output uses direct-address array index as the implicit group key`. |
| L3: No standalone `include_rows=False` timing | Closed by follow-up evidence | Goal3203 records a count-only timing probe with validation separated from measured no-row repetitions. |
| L4: Goal3201 small-scale non-monotonicity needs context | Bounded by follow-up evidence | Goal3203 and Goal3205 separate validation, no-row timing, and reusable prepared-handle timing; the reports treat 512-row behavior as internal timing only and do not use it as public evidence. |

## Boundary

This intake does not authorize release, public speedup claims, broad RT-core
claims, true zero-copy claims, or RayJoin paper reproduction claims.

The chain remains internal evidence for a generic primitive route:

- generic segment-pair candidate device columns,
- generic dense/compact grouped-count device columns,
- Python-owned RayJoin route policy and left-ID remapping,
- Python-owned prepared-handle reuse.
