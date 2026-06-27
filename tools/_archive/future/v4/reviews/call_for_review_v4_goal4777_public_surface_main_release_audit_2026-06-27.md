# Call For Review - V4 Goal4777 Public-Surface Main Release Audit

Date: 2026-06-27

Requested verdict labels:

- `approve_goal4777_public_surface_release_audit`
- `approve_with_required_amendments`
- `reject_overclaim_or_public_surface_incoherent`
- `blocked_needs_more_evidence`

## Context

The bounded `v4.0.0` public tag has already been created and pushed:

```text
v4.0.0 -> 1c8f63cbadbb1edfc994c1c2477a94a7f00a8639
```

The tag was authorized by:

```text
future/v4/reviews/antigravity_v4_gemini_full_coverage_review_2026-06-27.md
verdict: approve_close_gemini_debt_and_allow_v4_0_public_tag
```

The final tag target had:

- focused release gates: `12 tests OK`;
- full V4 discovery before tag: `645 tests OK, skipped=1`;
- clean checkout;
- wheel build;
- installed-wheel smoke passing.

After tag creation, the public surface still had some pre-tag wording such as
"release candidate" and "tag target ready". Goal4777 fixes that live public
surface without moving or rewriting the already pushed tag.

## Files To Review

Primary audit:

- `future/v4/v4_goal4777_public_surface_main_release_audit_2026-06-27.md`

Current public docs:

- `README.md`
- `docs/current_v4_status.md`
- `docs/app_level_benchmark_summary.md`
- `docs/learn/performance_wording.md`
- `tutorials/current/01_first_run.md`
- `tutorials/current/02_hello_world.md`
- `tutorials/current/05_measurement_boundaries.md`
- `future/v4/README.md`

Current public front door and gates:

- `src/rtdsl/v4.py`
- `future/v4/examples/v4_frontdoor_quickstart.py`
- `scripts/v4_catalog_regression_gate.py`
- `src/rtdsl/v4_goal4773_release_authorization_status.py`

Tests:

- `tests/v4_frontdoor_test.py`
- `tests/v4_catalog_regression_gate_test.py`
- `tests/v4_goal4640_public_docs_cleanup_test.py`
- `tests/v4_goal4643_publication_decision_test.py`
- `tests/v4_goal4646_pretag_wording_fixes_test.py`
- `tests/v4_goal4773_release_authorization_status_test.py`

## Local Results To Check

Public examples:

```text
all public examples passed
```

Focused public-surface and release-gate tests:

```text
Ran 23 tests in 31.007s
OK
```

Full V4 local discovery:

```text
Ran 645 tests in 92.488s
OK (skipped=1)
```

## Questions For Reviewer

1. Does Goal4777 correctly distinguish the published `v4.0.0` tag from broad
   speedup / Tier-3 / zero-copy / embedding claims?
2. Is it correct to avoid moving or rewriting the already pushed `v4.0.0` tag?
3. Are the public docs now coherent for a first-time user, without exposing
   confusing pre-tag candidate language in the current learning path?
4. Does the quickstart JSON now report release truth clearly enough?
5. Do the tests guard against regression back to "release candidate" wording?
6. Are any overclaims introduced by replacing "release candidate" with
   "published release"?
7. Are any old docs still dangerously exposed in the current public path?

## Non-Authorization

This review must not authorize:

- broad all-app speedup wording;
- broad V4-over-V2.14 or V4-over-V3 speedup wording;
- whole-application high-performance release wording;
- Tier-3 callback/PTX public support;
- raw OptiX callback support;
- public true-zero-copy claims;
- embedding/C ABI/non-Python host claims;
- public paper-reproduction speedup claims;
- moving or force-updating the already pushed `v4.0.0` tag.
