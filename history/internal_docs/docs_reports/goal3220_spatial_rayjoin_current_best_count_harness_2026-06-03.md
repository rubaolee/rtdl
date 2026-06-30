# Goal3220: Spatial RayJoin Current-Best Count Harness

Date: 2026-06-03

## Purpose

Goal3220 adds a current-best internal Spatial RayJoin count/parity harness after
the Goal3210-3218 dense left-id count work.

It does not rewrite historical Goal2799. Instead, it creates a new harness that
keeps the historical route stable and records the current best route policy:

- `pip`: existing prepared OptiX count route,
- `lsi`: new fused dense left-id count route,
- `overlay_seed`: existing prepared OptiX count route.

The harness is count/parity-only. Row overlay continuation remains out of scope.

Artifacts:

- `scripts/goal3220_spatial_rayjoin_current_best_count_harness.py`
- `docs/reports/goal3220_spatial_rayjoin_current_best_count_harness_2026-06-03.json`
- `docs/reports/goal3220_spatial_rayjoin_current_best_count_harness_2026-06-03.stdout`

## Pod Result

- Commit: `06d86d597574550cde3f3775b3fc6c975e380606`
- GPU: `NVIDIA A40, 570.211.01`
- Status: `pass`
- Warmup: `1`
- Repeat: `5`
- Include rows: `false`

| Workload | Route | Expected Count | Observed Count | Primary Phase Median (ms) |
| --- | --- | ---: | ---: | ---: |
| `pip` | `prepared_optix` | 6 | 6 | `prepared_query_sec`: 0.13361871242523193 |
| `lsi` | `prepared_optix_left_id_dense_count` | 1 | 1 | `left_id_count_device_columns_sec`: 0.12501701712608337 |
| `overlay_seed` | `prepared_optix` | 0 | 0 | `prepared_query_sec`: 0.006055459380149841 |

All three rows have `matches_cpu_reference: true`.

## Interpretation

Goal3220 moves the fixture-level Spatial RayJoin benchmark harness onto the
same best LSI count route proven by Goal3218. It is useful as the current
internal harness because it makes the recommended route policy explicit:
primitive-first, with the fused dense route only where it matches the app's
count contract.

The native boundary remains generic. The native engine sees prepared
point/shape, segment-pair, segment-pair left-id count, or shape-pair contracts.
RayJoin workload interpretation stays in Python.

## Boundary

This harness does not authorize release, public speedup claims, whole-app
speedup claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.

