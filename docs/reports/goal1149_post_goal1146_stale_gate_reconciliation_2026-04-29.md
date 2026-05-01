# Goal1149 Post-Goal1146 Stale Gate Reconciliation

Date: 2026-04-29

## Scope

Goal1149 reconciles stale local gates after Goal1146 promoted two bounded public RTX wordings:

- `facility_knn_assignment / coverage_threshold_prepared_recentered`
- `barnes_hut_force_app / node_coverage_prepared_rich`

It preserves the robot hold:

- `robot_collision_screening / prepared_pose_flags` remains `public_wording_blocked`.

This goal does not run cloud, does not create new RTX timing evidence, does not authorize release, and does not broaden any public speedup claim.

## Changes

- Regenerated the Goal939 current RTX claim-review package from live matrices.
- Regenerated the Goal947 public v1.0 RTX app status page from live matrices.
- Regenerated the Goal1109 readiness report after Goal1146.
- Reconciled the robot cloud policy wording so it still names Goal1048, Goal1058, Goal1135, Goal1136, and Goal1142 while explicitly saying the accepted robot evidence is bounded sub-path evidence and public speedup wording remains blocked.

## Current Public Wording State

| App/path | Status | Public wording boundary |
| --- | --- | --- |
| `facility_knn_assignment / coverage_threshold_prepared_recentered` | `public_wording_reviewed` | Prepared recentered coverage-threshold query decision only; ranked KNN assignment, fallback assignment, Python setup, and whole-app speedup remain outside. |
| `barnes_hut_force_app / node_coverage_prepared_rich` | `public_wording_reviewed` | Prepared depth-8 node-coverage threshold traversal only; opening-rule evaluation, candidate rows, force-vector reduction, N-body simulation, and whole-app speedup remain outside. |
| `robot_collision_screening / prepared_pose_flags` | `public_wording_blocked` | Same-source evidence review is accepted, but public speedup wording remains blocked pending same-total-work or explicit normalized-baseline review. |

## Verification

Focused stale-gate reconciliation:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal939_current_rtx_claim_review_package_test tests.goal1044_public_rtx_cloud_policy_sync_test -v
```

Result: 8 tests OK.

Expanded public RTX documentation and policy slice:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1109_v1_rtx_readiness_status_after_baselines_test \
  tests.goal1010_public_rtx_readme_wording_test \
  tests.goal1011_rtx_public_wording_matrix_test \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal1020_public_docs_rtx_boundary_audit_test \
  tests.goal1024_final_public_surface_audit_test \
  tests.goal515_public_command_truth_audit_test \
  tests.goal687_app_engine_support_matrix_test \
  tests.goal939_current_rtx_claim_review_package_test \
  tests.goal1044_public_rtx_cloud_policy_sync_test \
  tests.goal1123_public_wording_review_after_goal1121_test \
  tests.goal1126_robot_normalized_public_wording_review_test -v
```

Result: 44 tests OK.

## Consensus Status

Codex local verdict: ACCEPT.

External-AI review status: pending. Goal1146 itself has Gemini manual ACCEPT and Codex consensus; this Goal1149 reconciliation still needs a bounded Gemini or Claude review before closure under the project 2-AI rule.

