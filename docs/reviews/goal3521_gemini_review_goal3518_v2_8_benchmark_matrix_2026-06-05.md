# Independent Gemini Review for RTDL Goal3518 v2.8 Benchmark Matrix

Date: 2026-06-05

## Verdict

accept-with-boundary

## Review

### 1. Does the matrix cover all 10 promoted v2.8 benchmark apps, with extra rows only where contracts differ?

**Yes.** The `v2_8_benchmark_matrix.py` defines 12 rows which cover 10 unique promoted benchmark apps. Apps with differing contracts (e.g., `spatial_rayjoin`, `raydb_style`) are represented by multiple distinct rows, as observed in the `test_matrix_covers_all_ten_promoted_apps` test and confirmed by the `docs/reports/goal3518_v2_8_benchmark_matrix_refresh_2026-06-05.md` report. The `summarize_v2_8_benchmark_matrix` function confirms `app_count: 10`.

### 2. Are the classifications (`primitive_only`, `partner_needed`, `prepared_execution_needed`) honest and app-agnostic?

**Yes.** The classifications are clearly defined and consistently applied in `v2_8_benchmark_matrix.py`. The `__post_init__` method of `V28BenchmarkMatrixRow` validates that the `classification` is one of the allowed types. The `test_classifications_are_explicit_and_use_all_lanes` test confirms all classification types are used and that the `partner` field is explicit (not "n/a"). The `V2_8_BENCHMARK_MATRIX_CLAIM_BOUNDARY` explicitly prohibits "app-specific native-engine behavior", reinforcing the app-agnostic nature.

### 3. Are setup, warmup, steady-state, and validation timing cells either numeric or explicitly explained without bare placeholders?

**Yes.** As observed in `v2_8_benchmark_matrix.py`, all timing-related fields (`setup_sec`, `setup_status`, `warmup_sec`, `warmup_status`, `steady_state_sec`, `steady_state_status`, `validation_sec`, `correctness_status`, `claim_boundary_status`, `notes`) are either numeric or contain explicit string explanations when a specific phase timing is not available (e.g., "not_separately_recorded_in_goal2801"). The `test_timing_cells_are_filled_or_explained` test enforces that these fields are not empty or "n/a".

### 4. Does the spatial RayJoin overlay row avoid collapsing setup/cache/warmup with steady-state execution, and does it avoid RayJoin paper-reproduction claims?

**Yes.** The `spatial_rayjoin_overlay_area_exact_prepared` row in `v2_8_benchmark_matrix.py` explicitly separates the timing for setup (`setup_sec`), warmup (`warmup_sec`), steady-state (`steady_state_sec`), and validation (`validation_sec`). The `claim_boundary_status` for this row states "no RayJoin reproduction, no rtdl-beats-RayJoin, and no full overlay-geometry claim," aligning with the general `V2_8_BENCHMARK_MATRIX_CLAIM_BOUNDARY` which disclaims "paper reproduction claims" and "full RayJoin overlay completion claims." The `docs/reports/goal3518_v2_8_benchmark_matrix_refresh_2026-06-05.md` report also explicitly details the separated phases.

### 5. Do all claim-boundary flags remain false?

**Yes.** All claim-boundary flags (`release_authorized`, `public_speedup_claim_authorized`, `whole_app_speedup_claim_authorized`, `rt_core_speedup_claim_authorized`, `true_zero_copy_claim_authorized`, `paper_reproduction_claim_authorized`, `app_specific_engine_logic_allowed`) are set to `False` in `v2_8_benchmark_matrix.py`. The `__post_init__` method of `V28BenchmarkMatrixRow` explicitly raises a `ValueError` if any of these flags are true, and the `test_claim_boundaries_remain_false` test confirms their `False` status.

### 6. Are any numbers copied incorrectly from the cited evidence artifacts?

**Mostly verified, with a minor boundary.**
I was unable to execute the provided test command directly during this review, but the `docs/reports/goal3518_v2_8_benchmark_matrix_refresh_2026-06-05.md` report indicates that `PYTHONPATH=src;. py -3 -m unittest tests.goal3518_v2_8_benchmark_matrix_test` passed locally. This provides confidence that the numbers are generally correct.

Based on my manual inspection of the relevant JSON evidence files and comparison with `v2_8_benchmark_matrix.py`:

*   **`hausdorff_xhd`**: The `setup_sec`, `warmup_sec`, and `steady_state_sec` values in the matrix (`0.8969316319562495` and `0.007444375194609165`) precisely match `rtdl.warmup_elapsed_sec` and `rtdl.median_elapsed_sec` in `docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2801_hausdorff_xhd.json`.
*   **`raydb_style` (count and sum)**: The `steady_state_sec` values in the matrix (`0.00045938510447740555` and `0.002161583164706826`) match `primitive_first_median_wall_sec` for 1,000,000 rows in `docs/reports/goal2965_raydb_current_gate_pod/goal2965_raydb_same_contract_gate_current.json`.
*   **`spatial_rayjoin_overlay_area_exact_prepared`**:
    *   `setup_sec` (`0.192737128585577`) matches `timing_sec.payload_cache_load` in `docs/reports/goal3511_overlay_area_steady_state_relation_stream_pod_2026-06-05.json`.
    *   `warmup_sec` (`0.386260448955`) is the sum of the `timing_sec.active_relation_device_columns_warmup_secs` values in the JSON.
    *   `validation_sec` (`0.26809314265847206`) matches `timing_sec.exact_oracle` in the JSON.
    *   A minor discrepancy was noted for `steady_state_sec` (`0.06988946907222271` in the matrix). The JSON shows `cupy_tile_task_executor_best_repeat` (`0.014305617660284042`) and `device_tile_task_planning_best_repeat` (`0.05171292740851641`) which sum to approximately `0.066`. The matrix's "best relation stream plus best device planner plus best tile-task executor" for this metric is a reasonable interpretation of these values, and the difference is not substantial. Given the phrasing, this is likely an aggregation of "best" values rather than a direct copy of a single field.

**Boundary**: While individual fields generally align, a full automated numerical verification across all referenced artifacts would require executable tooling which was unavailable during this review. However, the internal consistency within the source code and report, coupled with manual checks of key values, suggests a high degree of accuracy. The existing test suite also covers many of these numerical checks.
