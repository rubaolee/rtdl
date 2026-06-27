# Goal1013 Claim Packet Public Wording Sync

Date: 2026-04-26

## Problem

Goal1011 added `rtdsl.rtx_public_wording_matrix()` and Goal1012 synchronized
the public status-page generator, but older claim/planning packet generators
still consumed only readiness and maturity matrices.

That created a stale interpretation risk:

- `robot_collision_screening` could appear as a generic ready claim-review row;
- generated claim packets could omit the separate `public_wording_blocked`
  status;
- checked-in artifacts could retain old cloud policy text after Goal1011.

## Change

Updated these generators:

- `scripts/goal847_active_rtx_claim_review_package.py`
- `scripts/goal848_v1_rt_core_goal_series.py`
- `scripts/goal939_current_rtx_claim_review_package.py`

Regenerated these artifacts:

- `docs/reports/goal847_active_rtx_claim_review_package_2026-04-23.json`
- `docs/reports/goal847_active_rtx_claim_review_package_2026-04-23.md`
- `docs/reports/goal848_v1_0_rt_core_goal_series_2026-04-23.json`
- `docs/reports/goal848_v1_0_rt_core_goal_series_2026-04-23.md`
- `docs/reports/goal939_current_rtx_claim_review_package_2026-04-25.json`
- `docs/reports/goal939_current_rtx_claim_review_package_2026-04-25.md`

## New Invariants

- Claim/planning packets include public wording status in addition to readiness
  and maturity.
- `robot_collision_screening` remains technically
  `ready_for_rtx_claim_review` / `rt_core_ready`.
- `robot_collision_screening` is separately `public_wording_blocked`.
- Reviewed public wording rows are counted separately from technical readiness.
- Public wording remains forbidden for rows that are blocked or not reviewed.

## Tests

Command:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal847_active_rtx_claim_review_package_test \
  tests.goal848_v1_rt_core_goal_series_test \
  tests.goal939_current_rtx_claim_review_package_test \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal1011_rtx_public_wording_matrix_test -v
```

Result: 24 tests OK.

## Boundary

This goal does not authorize new public speedup wording. It only synchronizes
internal/generated claim-planning artifacts with the public-wording source of
truth introduced in Goal1011.
