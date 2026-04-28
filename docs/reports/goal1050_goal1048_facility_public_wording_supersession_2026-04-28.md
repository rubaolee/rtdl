# Goal1050 Goal1048 Facility Public Wording Supersession

Date: 2026-04-28

## Verdict

ACCEPT as a current-doc supersession, pending external-style AI review for final
2-AI closure.

## Scope

This goal corrects current public RTX wording after the Goal1048 RTX A5000
artifact review. It does not rewrite historical external reviews. Historical
Goal1009 wording-review artifacts remain part of the audit trail, but their
facility wording conclusion is superseded for current public docs because the
newer Goal1048 evidence used skip-validation for the facility group.

## Findings

- `facility_knn_assignment / coverage_threshold_prepared` remains a real
  bounded RT-core path.
- It must not be listed as reviewed public RTX speedup wording after Goal1048.
- The current public wording count is now 6 reviewed rows and 2 blocked rows.
- The blocked rows are `facility_knn_assignment` and
  `robot_collision_screening`.
- `robot_collision_screening` remains blocked because of the existing timing
  floor and skip-validation boundary.
- `facility_knn_assignment` is diagnostic-only until rerun with validation
  enabled and then reviewed against same-semantics baselines.

## Changes Made

- Updated `rtdsl.rtx_public_wording_matrix()` so
  `facility_knn_assignment` is `public_wording_blocked` with Goal1048 evidence.
- Updated `rtdsl.rt_core_app_maturity_matrix()` cloud policies from stale
  Goal1043 pending-rerun language to Goal1048 completed-rerun language.
- Kept validated/strict bounded sub-paths separate from diagnostic-only paths.
- Regenerated current Goal848, Goal947, Goal939, and Goal1046/Goal1025-derived
  artifacts from the source matrices.
- Updated README and current public status docs to remove facility from the
  reviewed public RTX wording list.
- Updated tests so the source-of-truth expectation is 6 reviewed public wording
  rows and 2 blocked public wording rows.

## Non-Changes

- Historical Goal1009 artifacts were not rewritten.
- No release authorization was added.
- No whole-app speedup claim was added.
- No claim was made that `--backend optix` alone proves public RTX speedup.

## Verification

Focused synchronization tests pass:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal1044_public_rtx_cloud_policy_sync_test \
  tests.goal1011_rtx_public_wording_matrix_test \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal1025_pre_cloud_rtx_app_batch_readiness_test \
  tests.goal939_current_rtx_claim_review_package_test \
  tests.goal1010_public_rtx_readme_wording_test \
  tests.goal848_v1_rt_core_goal_series_test \
  tests.goal705_optix_app_benchmark_readiness_test
```

Result: 41 tests, OK.

## Closure Rule

This goal should be called closed only after an external-style AI reviewer
confirms that current docs, generators, and tests consistently treat facility
public wording as blocked after Goal1048.
