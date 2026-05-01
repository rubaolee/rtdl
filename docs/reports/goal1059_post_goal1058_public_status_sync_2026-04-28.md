# Goal1059 Post-Goal1058 Public Status Sync

Date: 2026-04-28

## Boundary

This goal refreshes current public/status wording after the Goal1058 RTX A5000
artifact-intake and three-AI same-semantics consensus. It does not authorize
release, public RTX speedup wording, or broad whole-app RTX claims.

## Changes

- Updated `rtdsl.rtx_public_wording_matrix()` for
  `facility_knn_assignment` and `robot_collision_screening` so the source of
  truth no longer says the current blocker is missing validation from the old
  Goal1048 skip-validation run.
- Updated the corresponding readiness evidence labels so the generated status
  page does not diverge from the Goal1058 evidence anchor.
- Preserved `public_wording_blocked` for both apps because Goal1058 validated
  oracle parity but did not authorize timing/baseline speedup wording.
- Regenerated `docs/v1_0_rtx_app_status.md` and the Goal947 JSON artifact from
  the updated matrix.
- Refreshed `README.md`, `docs/app_engine_support_matrix.md`, and the generated
  Goal1051 follow-up report so current docs point at Goal1058 instead of stale
  skip-validation wording.

## Current Truth

| App | Current evidence | Public speedup wording |
| --- | --- | --- |
| `facility_knn_assignment` | Goal1058 validated `coverage_threshold_prepared` oracle parity on RTX A5000. | Still blocked; no separate timing/baseline wording review has authorized a public speedup claim. |
| `robot_collision_screening` | Goal1058 validated `prepared_pose_flags` oracle parity on RTX A5000. | Still blocked; timing-floor and baseline evidence still need review before public speedup wording. |

## Verification

Focused tests passed:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1011_rtx_public_wording_matrix_test \
  tests.goal1010_public_rtx_readme_wording_test \
  tests.goal1044_public_rtx_cloud_policy_sync_test \
  tests.goal1025_pre_cloud_rtx_app_batch_readiness_test \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal1051_post_goal1048_followup_plan_test
```

Result: `25` tests passed.

After external review, the focused suite was expanded to include the OptiX app
benchmark-readiness tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1044_public_rtx_cloud_policy_sync_test \
  tests.goal1011_rtx_public_wording_matrix_test \
  tests.goal1010_public_rtx_readme_wording_test \
  tests.goal1025_pre_cloud_rtx_app_batch_readiness_test \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal1051_post_goal1048_followup_plan_test \
  tests.goal705_optix_app_benchmark_readiness_test
```

Result: `34` tests passed.

## External Review

- Claude: `ACCEPT`, with two non-blocking notes. The unreachable test branch
  was fixed after the review, and the readiness evidence label divergence was
  corrected.
- Gemini: `ACCEPT`, after the Claude-note test fix, confirming the Goal1058
  oracle-parity anchor and continued public wording block.

## Non-Claims

- No public speedup claims are authorized.
- No whole-app speedup claims are authorized.
- Goal1007 historical large-repeat commands can still contain
  `--skip-validation`; those are older large-scale performance commands and are
  not the current validation status for facility or robot.
