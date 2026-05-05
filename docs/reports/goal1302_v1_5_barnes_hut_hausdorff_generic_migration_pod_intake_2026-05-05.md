# Goal1302 Pod Intake: Barnes-Hut And Hausdorff Generic Migration

Date: 2026-05-05

## Scope

Goal1302 migrates two fixed-radius prepared OptiX decision paths onto the
Goal1298 generic scalar threshold-count primitive:

- `barnes_hut_force_app / node_coverage_prepared`
- `hausdorff_distance / directed_threshold_prepared`

This is internal v1.5 migration evidence only.

## Source

Pod source commit:

```text
9ff886a6a1bed9a61934ef72667fa332823977b2
```

## Result

| App | OptiX path | Scale | Generic primitive | Summary primitive | Parity | RT core |
| --- | --- | --- | --- | --- | --- | --- |
| `barnes_hut_force_app` | `node_coverage_prepared` | 4096 bodies, 4 nodes | `FIXED_RADIUS_COUNT_THRESHOLD_2D` | `REDUCE_INT(COUNT)` | `matches_oracle=true` | `true` |
| `hausdorff_distance` | `directed_threshold_prepared` | 4096 A points, 4096 B points | `FIXED_RADIUS_COUNT_THRESHOLD_2D` | `REDUCE_INT(COUNT)` | `matches_oracle=true` | `true` |

Focused pod tests:

```text
Ran 15 tests in 0.381s

OK
```

## Artifacts

Copied compact pod artifacts:

```text
docs/reports/goal1302_v1_5_barnes_hut_hausdorff_generic_migration_pod_results/compact_summary.json
docs/reports/goal1302_v1_5_barnes_hut_hausdorff_generic_migration_pod_results/source_commit.txt
docs/reports/goal1302_v1_5_barnes_hut_hausdorff_generic_migration_pod_results/unittest_goal1302.txt
```

## Boundary

The result proves the migrated bounded fixed-radius threshold-decision paths
use the generic primitive and preserve oracle parity on an RTX pod. It does not
claim Barnes-Hut opening-rule evaluation, force-vector reduction, exact
Hausdorff distance, nearest-neighbor row speedup, whole-app acceleration, or
public NVIDIA speedup wording.
