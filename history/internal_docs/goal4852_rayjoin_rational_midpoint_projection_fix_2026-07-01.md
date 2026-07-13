# Goal4852: RayJoin Rational Midpoint Projection Fix

Date: 2026-07-01

## Purpose

Close the exact-paper regression identified during the Goal4851 review: one
`tests.goal4374_rayjoin_exact_paper_suite_test` assertion failed by about
`8e-14` in output-chain midpoint projection.

## Root Cause

`_midpoints_for_sorted_xsects()` used rational LSI intersection coordinates, but
it converted each rational intersection coordinate to an internal integer first
and only then averaged the two integer coordinates:

`trunc(left) + trunc(right) -> midpoint`

The intended RayJoin-style behavior for output-chain midpoint projection is:

`midpoint(left_rational, right_rational) -> trunc once`

For values such as `100.9` and `101.1`, the old order produced `100`; the
correct midpoint-before-truncation order produces `101`.

## Change

Updated the rational branch in `src/rtdsl/rayjoin_overlay.py` so midpoint
projection averages `Fraction` coordinates first, then applies
`_rayjoin_author_rational_to_internal()` once.

This is a narrow correctness fix for author-scaled output-chain midpoint
projection. It does not alter LSI candidate generation, PIP semantics, or the
public planar-map LSI count primitive.

## Verification

Local:

- `PYTHONPATH=src py -m unittest tests.goal4374_rayjoin_exact_paper_suite_test -v`
  - 28 tests passed.
- `PYTHONPATH=src py -m unittest tests.goal4851_planar_map_lsi_public_front_door_test tests.goal4845_rayjoin_lsi_collapsed_ray_candidate_test`
  - 4 tests passed, 1 skipped.
- `git diff --check -- src/rtdsl/rayjoin_overlay.py`
  - no whitespace errors.

POD:

- Host: `root@157.157.221.29 -p 23132`
- Worktree: `/workspace/rtdl_goal4817_user_smoke_20260630_102224`
- Command:
  `PYTHONPATH=src python3 -m unittest tests.goal4374_rayjoin_exact_paper_suite_test -v`
- Result:
  28 tests passed.

## Boundary

This fixes a local exact-paper regression guard. It does not authorize:

- full Section 5.7 paper reproduction,
- broad RayJoin performance claims,
- public speedup wording,
- or new claims for the count-only planar-map LSI primitive.
