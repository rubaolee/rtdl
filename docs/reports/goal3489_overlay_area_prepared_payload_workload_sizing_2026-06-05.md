# Goal3489 - Overlay-Area Prepared Payload Workload Sizing

## Status

Implemented locally; pod evidence pending.

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

## Validation

Local validation:

- `py -3 -m unittest tests.goal3489_overlay_area_prepared_payload_workload_sizing_test`

Pod validation should save:

- `docs/reports/goal3489_overlay_area_prepared_payload_workload_sizing_pod_2026-06-05.json`

