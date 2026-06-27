# Goal 774: RTX Manifest Duplicate Command Reuse

Date: 2026-04-23

## Verdict

`IMPLEMENTED`

The RTX cloud runner now reuses duplicate manifest commands during a single Goal761 run. This prevents the Outlier and DBSCAN manifest entries from executing the same combined Goal757 fixed-radius profiler twice on paid GPU time.

## Problem

The Goal759 manifest intentionally contains separate app entries for:

- `outlier_detection`
- `dbscan_clustering`

Both entries point at the same combined profiler command:

```text
python3 scripts/goal757_optix_fixed_radius_prepared_perf.py ...
```

Before Goal774, Goal761 executed each manifest entry independently, so a full cloud run could run the same combined fixed-radius benchmark twice and overwrite the same output JSON twice.

## Change

`scripts/goal761_rtx_cloud_run_all.py` now caches command results by the exact command tuple during one runner invocation.

- First occurrence: `execution_mode: executed`
- Duplicate occurrence: `execution_mode: reused_command_result`

The summary still preserves one logical result row per manifest entry, so Goal762 and downstream review can keep separate app claim scopes.

## Why This Matters

This is a direct cloud-cost and benchmark-time reduction. It does not change app semantics, result parsing, or claim boundaries. It only avoids repeating identical work.

## Verification

Focused tests passed:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal761_rtx_cloud_run_all_test \
  tests.goal762_rtx_cloud_artifact_report_test \
  tests.goal769_rtx_pod_one_shot_test

Ran 6 tests in 0.446s
OK
```

Dry-run duplicate check:

```text
PYTHONPATH=src:. python3 scripts/goal761_rtx_cloud_run_all.py \
  --dry-run \
  --only outlier_detection \
  --only dbscan_clustering \
  --output-json /tmp/goal761_dedupe_test.json
```

Result:

```text
entry_count: 2
unique_command_count: 1
execution modes: executed, reused_command_result
```

Mechanical diff check passed:

```text
git diff --check
```

## Claim Boundary

This goal does not add performance evidence and does not authorize RTX speedup claims. It only reduces duplicate benchmark execution in the cloud pipeline.
