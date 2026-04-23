# Goal838 Local Baseline Collection Manifest

Status: implemented.

## Purpose

Goal836 says 23 baseline artifacts are missing before an RTX speedup claim package can be complete. Goal838 classifies those 23 required baselines into practical next actions without starting cloud or running heavy benchmarks.

## Implementation

- Added `/Users/rl2025/rtdl_python_only/scripts/goal838_local_baseline_collection_manifest.py`.
- Added `/Users/rl2025/rtdl_python_only/tests/goal838_local_baseline_collection_manifest_test.py`.
- Generated `/Users/rl2025/rtdl_python_only/docs/reports/goal838_local_baseline_collection_manifest_2026-04-23.json`.
- Generated `/Users/rl2025/rtdl_python_only/docs/reports/goal838_local_baseline_collection_manifest_2026-04-23.generated.md`.

## Current Classification

- `local_command_ready`: 6
- `linux_postgresql_required`: 2
- `collector_needed`: 4
- `optional_dependency_or_reference_required`: 2
- `deferred_until_app_gate_active`: 9

The six local-ready commands cover:

- DB sales-risk CPU compact summary.
- DB sales-risk Embree compact summary.
- DB regional-dashboard CPU compact summary.
- DB regional-dashboard Embree compact summary.
- Outlier Embree scalar fixed-radius summary.
- DBSCAN Embree scalar fixed-radius summary.

The collector-needed items are:

- Outlier CPU scalar threshold-count oracle.
- DBSCAN CPU scalar threshold-count oracle.
- Robot CPU pose-count oracle.
- Robot Embree any-hit pose-count compact summary.

## Important Boundary

Goal838 does not run heavy benchmarks, does not write schema-valid baseline artifacts, does not start cloud resources, and does not authorize speedup claims. It only converts the Goal835/Goal836 requirements into an execution checklist with exact artifact paths and scale-safe commands.

## Verification

```bash
PYTHONPATH=src:. python3 -m unittest -v tests.goal838_local_baseline_collection_manifest_test
```

Result:

```text
Ran 4 tests in 0.195s
OK
```
