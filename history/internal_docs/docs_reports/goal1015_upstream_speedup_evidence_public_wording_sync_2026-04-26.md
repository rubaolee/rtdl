# Goal1015 Upstream Speedup Evidence Public Wording Sync

Date: 2026-04-26

## Problem

Goal1014 synchronized the staged wording gates, but two upstream evidence
artifacts still appeared earlier in the same chain:

- `docs/reports/goal971_post_goal969_baseline_speedup_review_package_2026-04-26.json`
- `docs/reports/goal1005_post_a5000_speedup_candidate_audit_2026-04-26.json`

These artifacts are evidence and candidate-classification packages, not final
release-facing wording sources. Without an explicit current wording field, a
reader could still see `robot_collision_screening` as a candidate in Goal1005
without also seeing that current public wording remains blocked.

## Change

Updated generators:

- `scripts/goal971_post_goal969_baseline_speedup_review_package.py`
- `scripts/goal1005_post_a5000_speedup_candidate_audit.py`

Regenerated artifacts:

- `docs/reports/goal971_post_goal969_baseline_speedup_review_package_2026-04-26.json`
- `docs/reports/goal971_post_goal969_baseline_speedup_review_package_2026-04-26.md`
- `docs/reports/goal1005_post_a5000_speedup_candidate_audit_2026-04-26.json`
- `docs/reports/goal1005_post_a5000_speedup_candidate_audit_2026-04-26.md`

## New Invariants

- Both artifacts declare
  `current_public_wording_source = rtdsl.rtx_public_wording_matrix()`.
- Every row carries `current_public_wording_status` and
  `current_public_wording_boundary`.
- `robot_collision_screening` can remain a historical technical candidate in
  Goal1005 while its current public wording status is explicitly
  `public_wording_blocked`.
- No public speedup claim is authorized by Goal971 or Goal1005.

## Tests

Command:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal971_post_goal969_baseline_speedup_review_package_test \
  tests.goal1005_post_a5000_speedup_candidate_audit_test \
  tests.goal1006_public_rtx_claim_wording_gate_test \
  tests.goal1011_rtx_public_wording_matrix_test -v
```

Result: 17 tests OK.

## Boundary

This goal does not change RTX readiness, speedup evidence, or public wording.
It only attaches the current public-wording source of truth to upstream evidence
packages so they cannot be mistaken for release-facing claim authorization.
