# Goal998 Current Claim-Packet Scalar Wording Resync

Date: 2026-04-26

## Scope

Resync current claim-review and speedup-audit packets after Goal992 made the
public fixed-radius claim paths explicit scalar outputs:

- Outlier: `density_count` / scalar threshold-count
- DBSCAN: `core_count` / scalar core-count

## Changes

- Updated `scripts/goal847_active_rtx_claim_review_package.py` so fixed-radius
  rows use current scalar claim scopes even when reading older cloud artifact
  rows that preserve historical wording.
- Updated `scripts/goal971_post_goal969_baseline_speedup_review_package.py`
  with the same scalar claim-scope normalization for post-Goal969 packages.
- Regenerated current generated packets:
  - `docs/reports/goal847_active_rtx_claim_review_package_2026-04-23.{json,md}`
  - `docs/reports/goal848_v1_0_rt_core_goal_series_2026-04-23.{json,md}`
  - `docs/reports/goal939_current_rtx_claim_review_package_2026-04-25.{json,md}`
  - `docs/reports/goal971_post_goal969_baseline_speedup_review_package_2026-04-26.{json,md}`
  - `docs/reports/goal978_rtx_speedup_claim_candidate_audit_2026-04-26.{json,md}`
- Strengthened tests for Goal847, Goal848, Goal939, Goal971, and Goal978 so
  fixed-radius rows must use scalar threshold-count/core-count language.

## Verification

Commands run:

```bash
PYTHONPATH=src:. python3 scripts/goal847_active_rtx_claim_review_package.py
PYTHONPATH=src:. python3 scripts/goal848_v1_rt_core_goal_series.py
PYTHONPATH=src:. python3 scripts/goal939_current_rtx_claim_review_package.py
PYTHONPATH=src:. python3 scripts/goal971_post_goal969_baseline_speedup_review_package.py
PYTHONPATH=src:. python3 scripts/goal978_rtx_speedup_claim_candidate_audit.py
PYTHONPATH=src:. python3 -m unittest \
  tests.goal847_active_rtx_claim_review_package_test \
  tests.goal848_v1_rt_core_goal_series_test \
  tests.goal939_current_rtx_claim_review_package_test \
  tests.goal971_post_goal969_baseline_speedup_review_package_test \
  tests.goal978_rtx_speedup_claim_candidate_audit_test
python3 -m py_compile \
  scripts/goal847_active_rtx_claim_review_package.py \
  scripts/goal848_v1_rt_core_goal_series.py \
  scripts/goal939_current_rtx_claim_review_package.py \
  scripts/goal971_post_goal969_baseline_speedup_review_package.py \
  scripts/goal978_rtx_speedup_claim_candidate_audit.py
git diff --check
```

Results:

- Focused tests: `Ran 19 tests`, `OK`
- Targeted stale-string scan over the regenerated current packets: no matches
- `py_compile`: passed
- `git diff --check`: passed

## Boundary

This goal updates current generated review packets and their generators only.
It does not rewrite historical cloud artifact reports such as Goal969 source
artifacts, does not run cloud/GPU workloads, and does not authorize public RTX
speedup claims.
