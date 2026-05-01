# Goal1064 RTX Runbook Sync After Goal1063

Date: 2026-04-28

## Summary

Updated `docs/rtx_cloud_single_session_runbook.md` so the current pod procedure
matches Goal1063:

- The current primary pod path is now Goal1062, not the older Goal1053
  11-command broad batch.
- The next paid pod should run only the remaining blocked
  `facility_knn_assignment` and `robot_collision_screening` rows.
- The runbook explicitly says rejected not-reviewed rows remain local-only until
  code or scale changes.
- Goal1062 correctness-validation rows must not use `--skip-validation`.
- Goal1062 large timing rows are timing-only and still require later
  artifact-intake plus 2+ AI review before any public wording changes.

## Files Updated

- `docs/rtx_cloud_single_session_runbook.md`
- `tests/goal829_rtx_cloud_single_session_runbook_test.py`

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal1062_blocked_rtx_wording_rerun_manifest_test \
  tests.goal1063_pre_pod_local_completion_audit_test
```

Result: `14 tests OK`.

Stale-primary-runner search:

```text
rg -n "Current Post-Goal1048 Runner|prefer the generated Goal1053 runner|bash scripts/goal1053_post_goal1048_cloud_batch_runner.sh|Goal1053 runs bootstrap|9 same-semantics review candidate commands|Copy back the entire Goal1052|Goal1056 local intake|For the current post-Goal1048" docs/rtx_cloud_single_session_runbook.md tests/goal829_rtx_cloud_single_session_runbook_test.py
```

Result: no matches.

## Boundary

This is a documentation and test sync only. It does not run cloud, change public
wording, authorize release, or authorize public RTX speedup claims.
