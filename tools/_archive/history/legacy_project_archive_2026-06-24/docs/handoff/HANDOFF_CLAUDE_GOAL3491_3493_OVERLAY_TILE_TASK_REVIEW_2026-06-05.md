# Handoff: Claude Review For Goals3491-3493 Overlay Tile-Task Chain

Please perform a read-only review of the recent v2.8 spatial-RayJoin overlay-area chain:

- Goal3491: `docs/reports/goal3491_overlay_area_tile_task_cupy_executor_2026-06-05.md`
- Goal3491 pod artifact: `docs/reports/goal3491_overlay_area_tile_task_cupy_executor_pod_2026-06-05.json`
- Goal3492: `docs/reports/goal3492_overlay_area_public_cdb_tile_task_executor_2026-06-05.md`
- Goal3492 pod artifact: `docs/reports/goal3492_overlay_area_public_cdb_tile_task_executor_pod_2026-06-05.json`
- Goal3493: `docs/reports/goal3493_overlay_area_active_shape_payload_construction_2026-06-05.md`
- Goal3493 pod artifact: `docs/reports/goal3493_overlay_area_active_shape_payload_construction_pod_2026-06-05.json`
- Implementation: `src/rtdsl/v2_8_overlay_area_prepared_payload.py`
- Runner: `scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py`
- Gap map: `src/rtdsl/v2_8_benchmark_runtime_gap.py`
- Tests: `tests/goal3491_overlay_area_tile_task_cupy_executor_test.py`, `tests/goal3492_overlay_area_public_cdb_tile_task_executor_test.py`, `tests/goal3493_overlay_area_active_shape_payload_construction_test.py`

Questions to answer:

1. Does the chain keep the native engine app-agnostic, with overlay-specific logic confined to Python/partner continuation scaffolding?
2. Does Goal3491 correctly prove the tile-task execution shape on CUDA fixtures without overclaiming release, RT-core speedup, true zero-copy, or full-overlay completion?
3. Does Goal3492 correctly prove the full public-CDB scalar exact-area stream against the Shapely/GEOS oracle, including the 9,653,005 triangle-pair workload and the 9.78e-9 total-area error?
4. Does Goal3493 correctly identify and improve the payload-construction bottleneck by preparing only active shapes, and are the timing/claim boundaries honest?
5. What are the remaining risks before this becomes an accepted v2.8 primitive/runtime direction, especially around prepared-payload residency/reuse, native-vs-partner acceptance, and full overlay-geometry output?

Please write the review to:

`docs/reviews/goal3494_claude_review_overlay_tile_task_chain_3491_3493_2026-06-05.md`

Use verdict values only from: `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`.
