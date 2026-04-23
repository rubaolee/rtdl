# Goal839 Local Active Baseline Collectors

Status: implemented.

## Purpose

Goal838 identified four active-path baseline artifacts as `collector_needed`:

- Outlier CPU scalar threshold-count oracle.
- DBSCAN CPU scalar threshold-count oracle.
- Robot CPU pose-count oracle.
- Robot Embree any-hit pose-count compact summary.

Goal839 implements those collectors and upgrades Goal838 so these baselines are now directly runnable as schema-valid local artifact writers.

## Implementation

Added:

- `/Users/rl2025/rtdl_python_only/scripts/goal839_baseline_artifact_schema.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal839_fixed_radius_baseline.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal839_robot_pose_count_baseline.py`
- `/Users/rl2025/rtdl_python_only/tests/goal839_local_baseline_collectors_test.py`

Updated:

- `/Users/rl2025/rtdl_python_only/scripts/goal838_local_baseline_collection_manifest.py`
- `/Users/rl2025/rtdl_python_only/tests/goal838_local_baseline_collection_manifest_test.py`
- regenerated `/Users/rl2025/rtdl_python_only/docs/reports/goal838_local_baseline_collection_manifest_2026-04-23.json`
- regenerated `/Users/rl2025/rtdl_python_only/docs/reports/goal838_local_baseline_collection_manifest_2026-04-23.generated.md`

## What The New Collectors Do

### Fixed-Radius CPU Oracles

`goal839_fixed_radius_baseline.py` writes Goal836-valid artifacts for:

- `outlier_detection / cpu_scalar_threshold_count_oracle`
- `dbscan_clustering / cpu_scalar_threshold_count_oracle`

The collector records:

- actual benchmark scale from the current run, not Goal835 target scale;
- repeated-run query timing;
- phase-separated metadata;
- compact summary output;
- validation against exact CPU reference logic.

### Robot CPU And Embree Compact Pose Counts

`goal839_robot_pose_count_baseline.py` writes Goal836-valid artifacts for:

- `robot_collision_screening / cpu_oracle_pose_count`
- `robot_collision_screening / embree_anyhit_pose_count_or_equivalent_compact_summary`

The Embree collector is explicit that it is an equivalent compact summary path, not a native scalar ABI.

## Important Honesty Fix

During implementation, a scale-identity bug was caught and fixed before commit: collector artifacts now record the actual run scale, not the Goal835 target scale. This matters because a small smoke artifact must not look like a 20k-copy or 200k-pose claim baseline.

## Goal838 Impact

Goal838 local baseline classification is now:

- `local_command_ready`: 10
- `linux_postgresql_required`: 2
- `optional_dependency_or_reference_required`: 2
- `deferred_until_app_gate_active`: 9

There are now zero active-path entries left in `collector_needed`.

## Verification

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal839_local_baseline_collectors_test \
  tests.goal838_local_baseline_collection_manifest_test \
  tests.goal836_rtx_baseline_readiness_gate_test
python3 -m py_compile \
  scripts/goal839_baseline_artifact_schema.py \
  scripts/goal839_fixed_radius_baseline.py \
  scripts/goal839_robot_pose_count_baseline.py \
  scripts/goal838_local_baseline_collection_manifest.py \
  tests/goal839_local_baseline_collectors_test.py \
  tests/goal838_local_baseline_collection_manifest_test.py
git diff --check
```

Result:

```text
Ran 14 tests in 0.493s
OK
```

`py_compile` and `git diff --check` passed.

## Boundary

Goal839 implements local artifact writers only. It does not claim that the large-scale required artifacts have already been collected, does not start cloud resources, and does not authorize RTX speedup claims.
