# Goal1303 Pod Intake: Robot Prepared Count Generic ANY_HIT Migration

Date: 2026-05-05

## Scope

Goal1303 migrates `robot_collision_screening / prepared_count` onto the v1.5
generic prepared ray/triangle primitive:

```text
ANY_HIT + COUNT_HITS
```

This is internal v1.5 migration evidence only. `prepared_pose_flags` remains
app-specific because grouped pose-flag reduction is not yet part of the generic
primitive ABI.

## Source

Pod source commit:

```text
9b6d401d27af83331610d420c1aac3be7d0a92fc
```

## Result

| App | OptiX path | Scale | Generic primitive | Summary primitive | Result |
| --- | --- | --- | --- | --- | --- |
| `robot_collision_screening` | `prepared_count` | 4096 poses, 16384 edge rays, 2048 obstacle triangles | `ANY_HIT` | `COUNT_HITS` | 11904 hit edges |

Focused pod tests:

```text
Ran 18 tests in 5.631s

OK
```

## Artifacts

Copied compact pod artifacts:

```text
docs/reports/goal1303_v1_5_robot_prepared_count_generic_migration_pod_results/compact_summary.json
docs/reports/goal1303_v1_5_robot_prepared_count_generic_migration_pod_results/source_commit.txt
docs/reports/goal1303_v1_5_robot_prepared_count_generic_migration_pod_results/unittest_goal1303.txt
```

## Boundary

The result proves the migrated scalar hit-edge count path uses the generic
prepared ray/triangle `ANY_HIT + COUNT_HITS` primitive on an RTX pod. It does
not claim pose-level flags, continuous collision detection, full robot
kinematics, mesh collision, whole-app acceleration, or public NVIDIA speedup
wording.
