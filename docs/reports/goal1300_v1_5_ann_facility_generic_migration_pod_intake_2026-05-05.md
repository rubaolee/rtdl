# Goal1300 Pod Intake: ANN And Facility Generic Fixed-Radius Migration

Date: 2026-05-05

## Scope

Goal1300 migrates two OptiX prepared threshold-decision app paths to the
Goal1298 generic fixed-radius threshold-count primitive:

- `ann_candidate_search / candidate_threshold_prepared`
- `facility_knn_assignment / coverage_threshold_prepared`

This is an internal v1.5 migration slice. It does not claim ANN indexing,
nearest-neighbor ranking, KNN assignment, facility optimization, whole-app
acceleration, or public NVIDIA speedup.

## Source

Pod source commit:

```text
0f6dea9142ffb595f296ce87f1361dee3cd0e66e
```

Pod command shape:

```text
PYTHONPATH=src:. python3 examples/rtdl_ann_candidate_app.py \
  --backend optix --copies 1024 \
  --optix-summary-mode candidate_threshold_prepared --require-rt-core

PYTHONPATH=src:. python3 examples/rtdl_facility_knn_assignment.py \
  --backend optix --copies 1024 \
  --optix-summary-mode coverage_threshold_prepared --require-rt-core
```

## Result

| App | OptiX path | Scale | Generic primitive | Summary primitive | Parity | RT core |
| --- | --- | --- | --- | --- | --- | --- |
| `ann_candidate_search` | `candidate_threshold_prepared` | 3072 queries, 3072 candidates | `FIXED_RADIUS_COUNT_THRESHOLD_2D` | `REDUCE_INT(COUNT)` | `matches_oracle=true` | `true` |
| `facility_knn_assignment` | `coverage_threshold_prepared` | 4096 customers, 4096 depots | `FIXED_RADIUS_COUNT_THRESHOLD_2D` | `REDUCE_INT(COUNT)` | `matches_oracle=true` | `true` |

Focused pod tests:

```text
Ran 15 tests in 0.014s

OK
```

## Artifacts

Copied pod artifacts:

```text
docs/reports/goal1300_v1_5_ann_facility_generic_migration_pod_results/ann_candidate_optix_threshold_1024.json
docs/reports/goal1300_v1_5_ann_facility_generic_migration_pod_results/facility_optix_coverage_threshold_1024.json
docs/reports/goal1300_v1_5_ann_facility_generic_migration_pod_results/source_commit.txt
docs/reports/goal1300_v1_5_ann_facility_generic_migration_pod_results/unittest_goal1300.txt
```

## Decision

Goal1300 is accepted as pod-verified internal v1.5 migration evidence for these
two prepared fixed-radius threshold-decision app paths. The next migration work
should continue converting app-named native paths into app-name-free generic
primitive entry points, while keeping public speedup claims behind separate
reviewed evidence and consensus.
