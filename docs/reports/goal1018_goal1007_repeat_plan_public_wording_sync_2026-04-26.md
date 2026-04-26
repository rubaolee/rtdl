# Goal1018 Goal1007 Repeat Plan Public Wording Sync

Date: 2026-04-26

## Problem

Goal1007 prepares larger-scale RTX repeats for rows held by Goal1006. After
Goal1011 introduced `rtdsl.rtx_public_wording_matrix()`, the repeat plan also
needed to show the current release-facing wording status for each target. This
matters most for `robot_collision_screening`: it is a legitimate repeat target,
but the current public wording status remains `public_wording_blocked` until a
larger repeat clears the 100 ms evidence gate and then passes review.

## Change

Updated:

- `scripts/goal1007_larger_scale_rtx_repeat_plan.py`
- `tests/goal1007_larger_scale_rtx_repeat_plan_test.py`

Regenerated:

- `docs/reports/goal1007_larger_scale_rtx_repeat_plan_2026-04-26.json`
- `docs/reports/goal1007_larger_scale_rtx_repeat_plan_2026-04-26.md`

## New Invariants

- The plan declares
  `current_public_wording_source = rtdsl.rtx_public_wording_matrix()`.
- Every target carries `current_public_wording_status` and
  `current_public_wording_boundary`.
- `robot_collision_screening / prepared_pose_flags` is a larger-repeat target
  and is simultaneously marked `public_wording_blocked`.
- Running the Goal1007 repeat commands still does not authorize public speedup
  wording.

## Tests

Command:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1007_larger_scale_rtx_repeat_plan_test \
  tests.goal1011_rtx_public_wording_matrix_test -v
```

Result: 10 tests OK.

## Boundary

This goal changes the repeat-plan metadata only. It does not run cloud
resources, does not collect new RTX evidence, and does not authorize public
speedup wording.
