# Goal3532 RayJoin Promoted-Contract Packet

Date: 2026-06-05

Status: internal evidence packet only. This report does not authorize release, public speedup wording, RayJoin paper reproduction claims, broad RT-core speedup claims, true zero-copy claims, or app-specific native-engine shortcuts.

## Purpose

Goal3524 exposed a weak blended RayJoin row (`1.096x`) that mixed count/parity, relation columns, shape-pair payloads, and overlay-area continuation into one hard-to-interpret number. Goal3530 required a promoted-contract preflight before measuring RayJoin again. Goal3532 implements that requirement by normalizing the runnable RayJoin v2.8 paths into one packet with separate rows per promoted contract.

The packet uses existing validated surfaces:

- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` for count/parity routes.
- `scripts/goal3465_rayjoin_relation_continuation_packet.py` for relation columns, grouped count, bounds-overlap payload, and witness payload.
- `scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py` for steady-state relation stream, device tile-task planning, and tile-task execution.

No native code was changed. The packet preserves the app-agnostic engine boundary by composing generic point/shape membership, segment-pair intersection, shape-pair relation columns, grouped count, payload, and overlay continuation contracts.

## A5000 Evidence

Artifact directory:

`docs/reports/goal3532_rayjoin_promoted_contract_packet_a5000_cdb_pair/`

Environment:

- Pod: `root@69.30.85.203 -p 22057`
- GPU: NVIDIA RTX A5000, driver 580.126.09, 24564 MiB
- RTDL commit: `98879336e041bff6363f0a18e3996953a021d53a`
- Dataset pair: `tests/fixtures/rayjoin/br_county_subset.cdb + tests/fixtures/rayjoin/br_county_subset.cdb`
- Note: the missing `data/rayjoin_public_cdb` files were not present on the pod or local checkout. The packet therefore uses the checked-in non-empty CDB fixture pair and labels rows as `cdb_pair`, not public-CDB evidence.
- Optional oracle tooling installed on pod during this run: `shapely==2.1.2`

## Promoted Rows

| Row | Contract | Primary metric sec | Metric source | Notes |
| --- | --- | ---: | --- | --- |
| `rayjoin_count_parity_pip_prepared_optix` | point closed-shape membership count | 0.000275 | `phases_sec.prepared_query_sec` | 9 positive assignments |
| `rayjoin_count_parity_lsi_left_id_dense_count` | segment-pair intersection count by left id | 0.059606 | `phases_sec.left_id_count_device_columns_sec` | 87 intersections |
| `rayjoin_count_parity_overlay_seed_active_count` | shape-pair active dependency count | 0.345494 | `phases_sec.active_count_device_continuation_sec` | 9 active seed pairs |
| `rayjoin_relation_columns_cdb_pair` | shape-pair relation device columns | 0.000532 | `relation_columns_sec.median` | 3 iterations, row counts stable |
| `rayjoin_relation_grouped_count_cdb_pair` | shape-pair relation grouped count by left | 0.000177 | `grouped_count_sec.median` | grouped sums match rows |
| `rayjoin_shape_pair_payload_bounds_cdb_pair` | bounds-overlap area payload | 0.000936 | `bounds_overlap_area_sec.median` | payload continuation row |
| `rayjoin_shape_pair_payload_witness_cdb_pair` | relation witness payload | 0.000721 | `witness_continuation_sec.median` | all witnesses resolved |
| `rayjoin_overlay_area_relation_stream_cdb_pair` | shape-pair relation stream steady-state | 0.000454 | `timing_sec.active_relation_device_columns` | exact oracle checked |
| `rayjoin_overlay_area_device_tile_planner_cdb_pair` | prepared overlay-area device tile-task planner | 0.001283 | `timing_sec.device_tile_task_planning_best_repeat` | 3 planner repeats |
| `rayjoin_overlay_area_tile_executor_cdb_pair` | prepared overlay-area tile-task executor | 0.001268 | `timing_sec.cupy_tile_task_executor_best_repeat` | 3 executor repeats |

Correctness checks:

- Relation continuation row counts: `[9, 9, 9]`
- Grouped-count sums match relation rows: `true`
- Relation witnesses resolved: `true`
- Overlay positive row-count match vs Shapely/GEOS oracle: `true`
- Overlay total area absolute error: `8.661876771398624e-12`
- Overlay max relation absolute error: `7.238779020646291e-12`

## Interpretation

The old single RayJoin number was too coarse. The promoted packet shows that the v2.8 relation-column, grouped-count, witness, bounds-payload, and overlay tile-task continuation pieces are runnable and mostly sub-millisecond on the checked-in CDB pair once the contract is isolated.

The packet also shows the honest remaining concern: count/parity setup and tiny-fixture launch overhead still dominate some rows. In particular, `rayjoin_count_parity_overlay_seed_active_count` is not a headline speedup row at this scale. The next promoted-path table should treat these count rows separately from continuation rows and should use larger resident datasets before drawing performance conclusions.

## Boundary

This is not a RayJoin paper reproduction and not a public speedup claim. It is an internal promoted-contract evidence packet used to repair Goal3524's blended RayJoin measurement problem under the Goal3527 recovery plan.
