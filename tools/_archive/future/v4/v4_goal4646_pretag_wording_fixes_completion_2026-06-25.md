# V4 Goal4646 Pre-Tag Wording Fixes Completion

Date: 2026-06-25

Status: `goal4646_pretag_wording_fixes_complete_tag_unblocked_by_wording_reviews`

## Purpose

Goal4646 closes Claude's public-tag blocker from
`docs/reviews/claude_v4_0_0_release_review_2026-06-25.md`.

The release substance remains accepted as a bounded operator release, but the
public tag wording had to stop implying unqualified high-performance or
near-handwritten-OptiX performance.

## Completed Fixes

Fix 1: label qualified.

- Current label:
  `RTDL v4.0.0 bounded operator release: 8 generic RT-core operators faster than brute-force partner/CPU baselines`
- Removed the previous unqualified label from current public docs, source
  release constants, quickstart payloads, and catalog-gate output.

Fix 2: distribution replaces geomean headline.

- Public docs now state: most measured operators are 1.2x-1.7x against stated
  brute-force partner/CPU baselines.
- Any-hit flags is listed separately as a larger `5.671x` operator win.
- Point-nearest and AABB are labeled as large scale-dependent
  algorithmic-complexity wins.
- The raw `5.1848067367961095x` scorecard geomean is retained only as internal
  scorecard math and is explicitly forbidden as the public headline.

Fix 3: denominators and scale are explicit.

- `src/rtdsl/v4_goal4639_release_scorecard_decision.py` now records
  `surface_denominators` for all eight surfaces.
- Public tables in `docs/current_v4_status.md`, `future/v4/README.md`,
  `future/v4/tier2_operator_catalog.md`, the Goal4639 decision, the Goal4642
  packet, and the Goal4639 evidence summary include baseline/denominator and
  scale columns.

## Files Changed

- `README.md`
- `docs/current_v4_status.md`
- `docs/learn/performance_wording.md`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`
- `future/v4/v4_goal4638_formal_release_scorecard_freeze_2026-06-25.md`
- `future/v4/v4_goal4639_serious_release_scorecard_pod_gate_decision_2026-06-25.md`
- `future/v4/v4_goal4642_final_3ai_release_authorization_packet_2026-06-25.md`
- `future/v4/v4_goal4643_publication_decision_2026-06-25.md`
- `future/v4/v4_goal4644_post_release_guardrails_2026-06-25.md`
- `future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25/summary.md`
- `scripts/v4_catalog_regression_gate.py`
- `src/rtdsl/v4.py`
- `src/rtdsl/v4_release_decision.py`
- `src/rtdsl/v4_scope.py`
- `src/rtdsl/v4_goal4638_formal_scorecard_freeze.py`
- `src/rtdsl/v4_goal4639_release_scorecard_decision.py`
- `src/rtdsl/v4_goal4642_final_authorization_packet.py`
- `src/rtdsl/v4_goal4643_publication_decision.py`
- `tests/v4_goal4646_pretag_wording_fixes_test.py`

## External Review

Claude review:

- `future/v4/reviews/claude_v4_goal4646_pretag_wording_fixes_review_2026-06-25.md`
- verdict: `accept_goal4646_wording_fixes_tag_unblocked`

Independent Codex review:

- `future/v4/reviews/codex_independent_v4_goal4646_pretag_wording_fixes_review_2026-06-25.md`
- verdict: `accept_goal4646_wording_fixes_tag_unblocked`

Antigravity:

- `future/v4/reviews/antigravity_v4_goal4646_pretag_wording_fixes_review_blocked_2026-06-25.md`
- status: `blocked_empty_output_not_counted_as_review`

Release-owner conclusion:

- Goal4646 wording fixes are complete;
- the public tag is unblocked by wording;
- Antigravity remains review debt only and does not weaken the completed
  wording gate.

## Verification

Targeted wording/release group:

```text
py -3 -m unittest tests.v4_goal4639_release_scorecard_decision_test \
  tests.v4_goal4646_pretag_wording_fixes_test \
  tests.v4_goal4640_public_docs_cleanup_test \
  tests.v4_frontdoor_test tests.v4_goal4632_release_decision_test \
  tests.v4_goal4642_final_authorization_packet_test \
  tests.v4_goal4643_publication_decision_test \
  tests.v4_goal4644_post_release_guardrails_test tests.v4_scope_gate_test
```

Result:

```text
Ran 39 tests
OK
```

Full V4 group:

```text
$mods = Get-ChildItem tests -Filter 'v4*_test.py' | ForEach-Object { 'tests.' + $_.BaseName }
py -3 -m unittest $mods
```

Result:

```text
Ran 185 tests
OK
```

Catalog gate:

```text
py -3 scripts/v4_catalog_regression_gate.py --mode dry-run --copies 16 --ray-count 16
```

Result:

```text
status: passed
authorized_release_label: RTDL v4.0.0 bounded operator release: 8 generic RT-core operators faster than brute-force partner/CPU baselines
```

Quickstart:

```text
py -3 examples/v4/v4_frontdoor_quickstart.py
```

Result:

```text
status: ok
authorized_release_label: RTDL v4.0.0 bounded operator release: 8 generic RT-core operators faster than brute-force partner/CPU baselines
```

Public-surface wording search:

```text
rg "RTDL v4\\.0\\.0 formal high-performance generic RT-core operator release|formal high-performance generic RT-core operator|near-OptiX performance from Python|Representative operator geomean" \
  README.md docs/current_v4_status.md docs/learn/performance_wording.md \
  future/v4/README.md future/v4/tier2_operator_catalog.md \
  future/v4/v4_goal4642_final_3ai_release_authorization_packet_2026-06-25.md \
  future/v4/v4_goal4643_publication_decision_2026-06-25.md \
  future/v4/v4_goal4644_post_release_guardrails_2026-06-25.md \
  scripts/v4_catalog_regression_gate.py src/rtdsl/v4.py \
  src/rtdsl/v4_release_decision.py src/rtdsl/v4_scope.py
```

Result: no matches.

## Goal-Level Decision Audit

Was I stupid?

No. This goal implements Claude's exact tag-blocking wording fixes instead of
arguing with the review or widening the release claim.

If yes, what actions would have made the decision stupid?

It would have been stupid to keep the unqualified high-performance label, to
headline the raw geomean, or to edit historical external review text as if the
reviewers had originally used the corrected label.

Was there another possibility that avoids getting stuck on a bad path?

Yes. Preserve historical review records as records, but supersede the public
tag wording through current docs, machine constants, and tests.

Can I start a different path that actually solves the problem?

Yes. The real path is now external review of this wording-fix completion,
followed by owner approval for the public tag.

## Non-Authorization

Goal4646 does not authorize broad/whole-application/all-benchmark speedup,
near-handwritten-OptiX wording, public true-zero-copy, Tier-3 callback support,
raw OptiX callback support, CuPy performance, C ABI, embedding, non-Python host
bindings, app-specific native kernels, Barnes-Hut coverage, Spatial RayJoin
coverage, or LibRTS paper reproduction.
