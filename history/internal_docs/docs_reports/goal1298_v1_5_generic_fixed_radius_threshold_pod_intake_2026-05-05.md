# Goal1298: Generic Fixed-Radius Threshold-Count Pod Intake

Date: 2026-05-05

## Source

- Commit: `f02310daaf9cc40beeedd24ec384649f55ee545c`
- Pod repo: `/workspace/rtdl_goal1292`
- Pod env: reused Goal1292 OptiX/CUDA environment from
  `docs/reports/goal1292_v1_5_generic_optix_pod_results/rtdl_pod_env.sh`

## Command

```text
PYTHONPATH=src:. python3 scripts/goal1298_v1_5_generic_fixed_radius_threshold_evidence.py \
  --copies 1024 \
  --backends cpu embree optix \
  --output docs/reports/goal1298_v1_5_generic_fixed_radius_threshold_pod_results/evidence.json
```

## Result

The generic fixed-radius threshold-count primitive passed CPU, Embree, and
OptiX parity at 1024 copies.

| Field | Value |
| --- | ---: |
| Query points | 2048 |
| Search points | 2048 |
| Expected threshold-reached count | 1024 |
| All parity checks passed | true |

Parity checks:

| Check | Result |
| --- | --- |
| CPU matches expected | true |
| Embree direct matches CPU rows | true |
| Embree direct matches expected | true |
| Embree prepared rows match direct | true |
| Embree prepared rows match expected | true |
| Embree prepared scalar matches expected | true |
| OptiX direct matches CPU rows | true |
| OptiX direct matches expected | true |
| OptiX prepared rows match direct | true |
| OptiX prepared rows match expected | true |
| OptiX prepared scalar matches expected | true |

Timing phases:

| Path | Threshold count | Key timing |
| --- | ---: | ---: |
| CPU direct | 1024 | query `0.24255216494202614s` |
| Embree direct | 1024 | query `0.1476686019450426s` |
| Embree prepared rows | 1024 | scene `0.036420827731490135s`, query `0.006930772215127945s` |
| Embree prepared scalar | 1024 | scene `0.036420827731490135s`, query `0.007546823471784592s` |
| OptiX direct | 1024 | query `0.8920944128185511s` |
| OptiX prepared rows | 1024 | scene `0.0022966116666793823s`, query `0.003938106819987297s` |
| OptiX prepared scalar | 1024 | scene `0.0022966116666793823s`, query `0.0017291642725467682s` |

Focused pod tests passed:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1298_v1_5_generic_fixed_radius_threshold_count_test \
  tests.goal1298_v1_5_generic_fixed_radius_threshold_evidence_test
```

Result: 9 tests OK.

## Artifacts

- `docs/reports/goal1298_v1_5_generic_fixed_radius_threshold_pod_results/evidence.json`
- `docs/reports/goal1298_v1_5_generic_fixed_radius_threshold_pod_results/source_commit.txt`
- `docs/reports/goal1298_v1_5_generic_fixed_radius_threshold_pod_results/unittest_goal1298.txt`

## Boundary

This is internal v1.5 generic primitive evidence. It validates a reusable
Embree/OptiX fixed-radius threshold-count primitive and scalar
`REDUCE_INT(COUNT)` output. It does not claim app-level ANN, DBSCAN, coverage,
Hausdorff, Barnes-Hut, whole-app, or public speedup performance.
