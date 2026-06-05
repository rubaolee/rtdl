# Goal3489 - Overlay-Area Prepared Payload Workload Sizing

## Status

Implemented and pod-validated.

Goal3489 measures the scale of the exact scalar overlay-area continuation after
Goal3488 showed that the current prepared simple-component payload covers all
positive public-CDB exact-area rows.

## Script

- `scripts/goal3489_overlay_area_prepared_payload_workload_sizing.py`

The script uses RTDL/OptiX to produce active relation ordinals, then uses the
same Shapely-normalized component classification as Goal3488 to measure:

- supported relation rows;
- expanded component-pair rows;
- total triangle-pair work;
- max triangle pairs in one relation row;
- p50/p90/p99 triangle-pair and component-pair counts.

## Why

Goal3488 showed the payload is feasible for the positive rows. Goal3489 answers
whether the next device continuation needs simple row-parallel execution or a
more serious tiling/paging strategy.

## Boundary

This is a workload-sizing probe, not a runtime implementation and not a
performance claim. It does not authorize release packaging, public speedup
wording, RT-core speedup wording, true-zero-copy wording, paper reproduction
claims, hidden dispatch, automatic partner selection, full overlay completion
claims, or app-specific native engine behavior.

## Pod Evidence

Artifact:

- `docs/reports/goal3489_overlay_area_prepared_payload_workload_sizing_pod_2026-06-05.json`

Pod result:

- active relation rows: `4,543`;
- supported rows: `4,539`;
- unsupported rows: `4`;
- expanded component-pair rows: `39,947`;
- total triangle pairs: `9,653,005`;
- max component-pair rows in one relation: `484`;
- max triangle pairs in one relation: `318,096`;
- triangle pairs per relation: p50 `294`, p90 `3,450`, p99 `25,530`;
- component pairs per relation: p50 `4`, p90 `20`, p99 `66`.

Interpretation: full public-CDB scalar exact area is not a hopelessly huge
all-pairs problem after RTDL relation discovery, but the long-tail rows require
real bounded tiling/paging. A one-thread-per-relation implementation will be
imbalanced; the next device path should split large relation rows into
component/tile tasks and then reduce by relation id.

## Validation

Local validation:

- `py -3 -m unittest tests.goal3489_overlay_area_prepared_payload_workload_sizing_test`

Pod validation saved:

- `docs/reports/goal3489_overlay_area_prepared_payload_workload_sizing_pod_2026-06-05.json`
