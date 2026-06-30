# Goal1213 Full Discovery Stale-Audit Repair

Date: 2026-05-01

## Purpose

This goal records the local full-discovery run after Goal1212 and the repair of
stale current-state audit expectations caused by the Goal1208 road-hazard
public wording promotion.

This is a local audit/test repair goal. It does not tag, release, publish, or
authorize broader RTX/RT-core public claims.

## Full Discovery Command

```bash
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -v
```

## Initial Full Discovery Result

- Tests run: `2366`
- Skipped: `196`
- Failures: `14`
- Errors: `8`

The failures were concentrated in stale audit/manifest expectations that still
assumed:

- `10` reviewed public RTX wording rows,
- `6` unresolved public-wording-evidence apps,
- road hazard still unresolved rather than Goal1208 reviewed,
- older post-Goal1048 pod batch counts of `9` commands/artifacts.

## Repairs

Updated current-state audit scripts and tests to the post-Goal1208 state:

- reviewed public wording rows: `11`,
- unresolved public-wording-evidence apps: `5`,
- road hazard removed from unresolved/pre-pod buckets,
- post-Goal1048 follow-up/manifest/runner/intake counts reduced from `9` to
  `8` where road hazard is no longer part of the unresolved same-semantics
  review batch,
- Goal1063 rejected not-reviewed row count reduced to `6`,
- Goal1133 now checks that public wording boundaries are respected, allowing
  the reviewed road-hazard narrow boundary while keeping the other tracked apps
  unpromoted.

## Files Changed

- `scripts/goal1025_pre_cloud_rtx_app_batch_readiness.py`
- `scripts/goal1051_post_goal1048_followup_plan.py`
- `scripts/goal1052_post_goal1048_cloud_batch_manifest.py`
- `scripts/goal1053_post_goal1048_cloud_batch_runner.py`
- `scripts/goal1063_pre_pod_local_completion_audit.py`
- `scripts/goal1125_unresolved_rtx_public_wording_prioritization.py`
- `scripts/goal1133_post_local_prep_audit.py`
- `scripts/goal1188_next_rtx_pod_gap_analysis.py`
- `tests/goal1025_pre_cloud_rtx_app_batch_readiness_test.py`
- `tests/goal1051_post_goal1048_followup_plan_test.py`
- `tests/goal1052_post_goal1048_cloud_batch_manifest_test.py`
- `tests/goal1053_post_goal1048_cloud_batch_runner_test.py`
- `tests/goal1056_post_goal1048_artifact_intake_test.py`
- `tests/goal1063_pre_pod_local_completion_audit_test.py`
- `tests/goal1125_unresolved_rtx_public_wording_prioritization_test.py`
- `tests/goal1133_post_local_prep_audit_test.py`
- `tests/goal1188_next_rtx_pod_gap_analysis_test.py`
- `tests/goal848_v1_rt_core_goal_series_test.py`
- `tests/goal939_current_rtx_claim_review_package_test.py`

## Targeted Validation Command

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1025_pre_cloud_rtx_app_batch_readiness_test \
  tests.goal1051_post_goal1048_followup_plan_test \
  tests.goal1052_post_goal1048_cloud_batch_manifest_test \
  tests.goal1053_post_goal1048_cloud_batch_runner_test \
  tests.goal1056_post_goal1048_artifact_intake_test \
  tests.goal1063_pre_pod_local_completion_audit_test \
  tests.goal1125_unresolved_rtx_public_wording_prioritization_test \
  tests.goal1133_post_local_prep_audit_test \
  tests.goal1188_next_rtx_pod_gap_analysis_test \
  tests.goal848_v1_rt_core_goal_series_test \
  tests.goal939_current_rtx_claim_review_package_test \
  -v
```

## Targeted Validation Result

- Tests run: `42`
- Result: `OK`

## Boundary

Goal1213 repairs stale current-state tests and audits only. It does not claim
that full discovery now passes; the full suite should be rerun after this
repair. It also does not authorize public wording beyond the already-reviewed
Goal1208 road-hazard boundary and the current `11` reviewed public RTX wording
rows.
