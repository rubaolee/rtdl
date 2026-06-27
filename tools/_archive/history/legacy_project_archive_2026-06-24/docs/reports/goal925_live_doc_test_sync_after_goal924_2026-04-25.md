# Goal 925: Live Doc/Test Sync After Goal924

Date: 2026-04-25

## Scope

Remove remaining stale live references to the old one-shot `Goal769` cloud
policy and old active/deferred counts after the Goal924 runbook refresh.

Historical reports are intentionally outside this goal. The current worktree
already contains unrelated dirty dated report artifacts; they are not edited,
staged, or claimed by this goal.

## Changes

- Updated `docs/app_engine_support_matrix.md` so the paid-pod procedure points
  to Goal824 local readiness, OptiX bootstrap, OOM-safe group execution,
  artifact copyback after every group, and shutdown.
- Updated `tests/goal830_rtx_goal_sequence_doc_sync_test.py` to check the
  current OOM-safe runbook policy rather than stale `one Goal769` wording.
- Updated `tests/goal835_rtx_baseline_collection_plan_test.py` to expect the
  current manifest-derived baseline plan:
  - active entries: `8`
  - deferred entries: `9`
  - total rows: `17`

## Verification

Focused test run:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal830_rtx_goal_sequence_doc_sync_test \
  tests.goal835_rtx_baseline_collection_plan_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal901_pre_cloud_app_closure_gate_test
```

Result: 20 tests OK.

Stale live-reference scan:

```bash
rg -n 'one Goal769|one full Goal769|Goal769 pod batch|5 active|12 deferred|active entries: `5`|deferred entries: `12`' \
  docs/app_engine_support_matrix.md \
  docs/goal_823_v1_0_nvidia_rt_core_app_promotion_plan.md \
  tests scripts README.md
```

Result: no matches.

`git diff --check` on the edited files: OK.

## Boundary

This goal only synchronizes live docs/tests with the current cloud protocol.
It does not stage historical reports, does not start cloud, does not promote
apps, and does not authorize RTX speedup claims. Pre-existing dirty dated
report artifacts remain outside scope and must not be included in the Goal925
commit.
