# Gemini Review for Goal3197 RayJoin Compact Grouped-Count Route (2026-06-03)

## Files Reviewed

- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `tests/goal3197_rayjoin_compact_grouped_count_route_test.py`
- `docs/reports/goal3197_rayjoin_compact_grouped_count_route_2026-06-03.md`
- `docs/reports/goal3197_rayjoin_compact_grouped_count_route_pod_2026-06-03.json`
- `docs/reports/goal3195_compact_grouped_count_timing_probe_2026-06-03.md`
- `docs/reports/goal3195_compact_grouped_count_timing_probe_2026-06-03.json`

## Questions Answered

### 1. Does Goal3197 keep native engine app-agnostic, with RayJoin interpretation and left-ID remapping staying in Python?
Yes. The `rtdl_rayjoin_v2_spatial_join_app.py` explicitly states in the `native_engine_boundary` for `run_rayjoin_prepared_optix_compact_grouped_count_workload` that "The engine sees generic segment-pair candidate columns and generic grouped-count compact columns. RayJoin workload interpretation and left-ID remapping stay in Python." The Python code also performs the left-ID remapping before passing data to RTDL and remaps it back for output. The test `tests/goal3197_rayjoin_compact_grouped_count_route_test.py` confirms this by checking for these phrases and the presence of `left_id_remap`.

### 2. Is the route correctly scoped as LSI-only and app-facing, not a native RayJoin extension?
Yes. The `rtdl_rayjoin_v2_spatial_join_app.py` function `run_rayjoin_prepared_optix_compact_grouped_count_workload` explicitly raises an error if the workload is not "lsi". The `docs/reports/goal3197_rayjoin_compact_grouped_count_route_2026-06-03.md` report states: "Scope is intentionally narrow: LSI workload only." and "This is an app-facing reference route, not a native app-specific extension." The test suite verifies this behavior.

### 3. Does the route use the Goal3193 compact resident grouped-count columns correctly and preserve false claim flags?
Yes. The `rtdl_rayjoin_v2_spatial_join_app.py` code calls `columns.grouped_count_by_left_id_compact_device_columns(...)`, directly utilizing the Goal3193 primitive. The `docs/reports/goal3197_rayjoin_compact_grouped_count_route_2026-06-03.md` report confirms that "compact group_key/count columns remain CUDA-resident" and explicitly lists several boundary flags (e.g., `public_speedup_claim_authorized`, `true_zero_copy_claim_authorized`) that remain `False`, indicating preservation of false claim flags. The test suite also verifies these flags.

### 4. Does the pod artifact prove only route correctness/metadata shape, not performance?
Yes. The `docs/reports/goal3197_rayjoin_compact_grouped_count_route_2026-06-03.md` report explicitly states: "This fixture is intentionally small. It proves route correctness and metadata shape, not performance." The `tests/goal3197_rayjoin_compact_grouped_count_route_test.py` validates correctness and metadata shape (e.g., `count_sum_matches_row_count`, `returned_rows_match_compact_row_count`) without asserting performance metrics.

### 5. Is the relationship with Goal3195 timing evidence clear: Goal3195 is the internal timing probe; Goal3197 is the fixture route correctness proof?
Yes. The `docs/reports/goal3197_rayjoin_compact_grouped_count_route_2026-06-03.md` report clarifies this relationship: "Goal3193 added generic compact grouped-count device columns. Goal3195 showed that this primitive path avoids large exact-row materialization when the app only needs per-left segment counts. Goal3197 exposes that primitive as an app-facing reference route...". This clearly delineates Goal3195 as the internal timing probe and Goal3197 as the app-facing fixture for correctness proof.

### 6. What should be the next engineering step for this RayJoin/segment-pair lane?
Based on the repeated emphasis in `docs/reports/goal3197_rayjoin_compact_grouped_count_route_2026-06-03.md` that the route "does not prove performance" and that "public speedup claim" flags are explicitly `False`, the next logical engineering step is to perform performance benchmarking. This would involve running this route on an RTX pod with larger datasets to gather evidence for potential speedup claims, similar to the `next_stage` described for the generic `prepared_optix` route.

## Verdict
accept-with-boundary

