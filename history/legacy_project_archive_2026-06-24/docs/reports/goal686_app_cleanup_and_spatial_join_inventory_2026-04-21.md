# Goal 686 App Cleanup And Spatial Join Inventory

## Scope

Goal686 cleans the public app surface after the v0.9.6 release line and answers
whether RTDL has spatial join apps.

## Changes

- Added `docs/application_catalog.md` as the public app inventory.
- Linked the catalog from `README.md`, `docs/README.md`,
  `docs/release_facing_examples.md`, and `examples/README.md`.
- Added `tests/goal686_app_catalog_cleanup_test.py` to keep the catalog,
  spatial-join inventory, and app-facing DB demo backend flag from drifting.
- Added `examples/rtdl_database_analytics_app.py` as the primary unified DB
  app over the regional-dashboard and sales-risk scenarios.
- Added `examples/rtdl_graph_analytics_app.py` as the primary graph app over
  BFS and triangle-count scenarios.
- Added `examples/rtdl_apple_rt_demo_app.py` as the primary Apple RT demo app
  over closest-hit and prepared visibility-count scenarios.
- Updated `tests/goal512_public_doc_smoke_audit_test.py` so the new catalog is
  covered by public markdown link smoke testing.
- Updated `tests/goal513_public_example_smoke_test.py` and
  `scripts/goal515_public_command_truth_audit.py` so new front-page commands
  are mechanically covered.
- Updated `examples/rtdl_v0_7_db_app_demo.py` to accept
  `--backend cpu_python_reference`, matching the common public example flag.
  The demo still reports canonical execution as `cpu_reference`.
- Refreshed `docs/reports/goal515_public_command_truth_audit_2026-04-17.*`
  after doc line-number changes. The audit result remains valid.

## Unified App Cleanup

- Primary DB app:
  - `examples/rtdl_database_analytics_app.py`
  - unifies `examples/rtdl_v0_7_db_app_demo.py` and
    `examples/rtdl_sales_risk_screening.py`
  - the older scenario-specific files remain runnable compatibility examples
- Primary graph app:
  - `examples/rtdl_graph_analytics_app.py`
  - unifies `examples/rtdl_graph_bfs.py` and
    `examples/rtdl_graph_triangle_count.py`
- Primary Apple RT app:
  - `examples/rtdl_apple_rt_demo_app.py`
  - unifies `examples/rtdl_apple_rt_closest_hit.py` and
    `examples/rtdl_apple_rt_visibility_count.py`
  - hardware-backed Apple execution remains explicitly conditional on macOS
    Apple Silicon and a rebuilt `librtdl_apple_rt`

## Spatial Join Answer

Yes. RTDL currently has spatial join apps and spatial-join-like public
examples:

- `examples/rtdl_service_coverage_gaps.py`: households join clinics by radius
  to find uncovered households.
- `examples/rtdl_event_hotspot_screening.py`: events self-join by radius to
  find hotspot events.
- `examples/rtdl_facility_knn_assignment.py`: customers join depots by nearest
  neighbor.
- `examples/rtdl_road_hazard_screening.py`: roads join hazard polygons by
  segment/polygon intersection count.
- `examples/rtdl_segment_polygon_hitcount.py`: direct segment/polygon
  hit-count join.
- `examples/rtdl_segment_polygon_anyhit_rows.py`: direct segment/polygon
  pair-emitting join.
- `examples/rtdl_polygon_pair_overlap_area_rows.py`: bounded polygon/polygon
  overlap join.
- `examples/rtdl_polygon_set_jaccard.py`: bounded polygon-set overlap/Jaccard
  join.

The catalog also records the SQL/PostGIS comparison boundary: PostGIS scripts
exist under `docs/sql/`, but PostGIS is an external baseline, not an RTDL
backend.

## Verification

Commands run from `/Users/rl2025/rtdl_python_only`:

```bash
PYTHONPATH=src:. python3 -m unittest -v tests.goal686_app_catalog_cleanup_test tests.goal513_public_example_smoke_test tests.goal505_v0_8_app_suite_test
```

Result: `11` tests OK.

After adding unified DB, graph, and Apple app entry points:

```bash
PYTHONPATH=src:. python3 -m unittest -v tests.goal686_app_catalog_cleanup_test tests.goal513_public_example_smoke_test tests.goal512_public_doc_smoke_audit_test
```

Result: `11` tests OK.

```bash
PYTHONPATH=src:. python3 -m unittest -v tests.goal512_public_doc_smoke_audit_test tests.goal654_current_main_support_matrix_test tests.goal685_engine_feature_support_contract_test
```

Result: `13` tests OK.

```bash
PYTHONPATH=src:. python3 -m unittest -v tests.goal512_public_doc_smoke_audit_test tests.goal686_app_catalog_cleanup_test
```

Result: `7` tests OK after adding the application catalog to public doc smoke.

```bash
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Result before unified app front-page commands: `valid: true`, `250` commands
across `14` public docs.

Result after adding unified DB and graph front-page commands:
`valid: true`, `252` commands across `14` public docs.

Manual JSON CLI smoke:

```bash
PYTHONPATH=src:. python3 examples/rtdl_v0_7_db_app_demo.py --backend cpu_python_reference
PYTHONPATH=src:. python3 examples/rtdl_service_coverage_gaps.py --backend cpu_python_reference
PYTHONPATH=src:. python3 examples/rtdl_event_hotspot_screening.py --backend cpu_python_reference
PYTHONPATH=src:. python3 examples/rtdl_facility_knn_assignment.py --backend cpu_python_reference
PYTHONPATH=src:. python3 examples/rtdl_road_hazard_screening.py --backend cpu_python_reference
PYTHONPATH=src:. python3 examples/rtdl_database_analytics_app.py --backend cpu_python_reference
PYTHONPATH=src:. python3 examples/rtdl_graph_analytics_app.py --backend cpu_python_reference
PYTHONPATH=src:. python3 examples/rtdl_apple_rt_demo_app.py
```

Result: every command emitted parseable JSON.

```bash
git diff --check
```

Result: clean.

## Boundary

- This is a public app cleanup and documentation inventory, not a new backend
  feature or performance claim.
- Spatial join examples are bounded RTDL workloads and apps, not a full GIS
  system.
- DB apps remain bounded analytical kernels, not SQL, indexes, transactions,
  query planning, or a DBMS.
- Graph apps remain bounded graph kernels, not a graph database or distributed
  graph analytics system.
- Apple RT app output can skip hardware sections when the Apple RT library is
  unavailable; that is an explicit availability boundary, not silent fallback.
