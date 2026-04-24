# Goal900 Pre-Cloud Gate Full-Batch Policy Sync

Date: 2026-04-24

## Result

The machine-readable pre-cloud readiness gate now matches the updated cloud
runbook policy.

## Change

`scripts/goal824_pre_cloud_rtx_readiness_gate.py` now emits this policy:

```text
Start one RTX cloud pod only after this gate is valid. Run one full Goal769 pod
batch with --include-deferred so active entries and deferred readiness gates
execute in the same paid pod session, collect the artifact bundle, then shut
down. Use --only only for same-pod targeted retry after a deferred gate fails.
```

This replaces the older active-first/deferred-optional wording.

## Refreshed Artifact

Command:

```bash
PYTHONPATH=src:. python3 scripts/goal824_pre_cloud_rtx_readiness_gate.py \
  --output-json docs/reports/goal900_pre_cloud_readiness_full_batch_policy_2026-04-24.json
```

Result:

```text
valid: true
active_count: 5
deferred_count: 12
full_batch_entry_count: 17
full_batch_unique_commands: 16
```

## Verification

Command:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal824_pre_cloud_rtx_readiness_gate_test \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal769_rtx_pod_one_shot_test
```

Result:

```text
11 tests OK
```

## Boundary

This is local readiness policy synchronization only. It does not start cloud and
does not authorize performance claims.
