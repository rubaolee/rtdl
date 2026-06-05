# Independent Gemini Review for Goal3474/3475 Exact Overlay Oracle

**Review Date:** 2026-06-05

## Summary

This review covers Goal3474, which implemented an exact overlay-area oracle using Shapely/GEOS for Spatial RayJoin active relation rows, and Goal3475, which updated the v2.8 benchmark runtime gap map to reflect the findings of Goal3474.

The primary purpose of Goal3474 is to provide a CPU-based correctness target for a future GPU-resident generic simple-polygon overlay-area continuation, rather than being an RTDL runtime dependency or performance path. Goal3475 ensures that the v2.8 gap map honestly reflects this distinction and the remaining engineering work.

All reviewed files (script, reports, and tests) consistently support the stated goals and boundaries of these initiatives.

## Review Questions

1.  **Does Goal3474 correctly use Shapely/GEOS only as an external CPU correctness oracle, not as an RTDL runtime dependency or performance path?**
    Yes, Goal3474 correctly uses Shapely/GEOS only as an external CPU correctness oracle. The script `scripts/goal3474_shape_pair_exact_overlay_area_shapely_oracle.py` explicitly handles Shapely as an optional dependency, raising a `RuntimeError` if not found and clarifying its role as "optional oracle dep, not as an RTDL runtime dependency." The `docs/reports/goal3474_shape_pair_exact_overlay_area_shapely_oracle_2026-06-05.md` report's "Boundary" section further reinforces this, stating "Shapely is optional external oracle tooling, not an RTDL runtime dependency and not a performance path." The JSON artifact confirms `oracle_dependency_scope: "external_cpu_correctness_oracle_not_rtdl_runtime_dependency"`. The test `tests/goal3474_shape_pair_exact_overlay_area_shapely_oracle_test.py` also validates these statements.

2.  **Does the pod artifact support the stated exact target: 4,543 active relation rows, 1,090 positive exact-area rows, 3,453 zero-area rows, 0 exceptions, and total exact area 26.08321766231042?**
    Yes, the pod artifact `docs/reports/goal3474_shape_pair_exact_overlay_area_shapely_oracle_pod_2026-06-05.json` fully supports the stated exact targets:
    *   `row_counts`: `[4543, 4543]` (4,543 active relation rows)
    *   `positive_area_row_counts`: `[1090, 1090]` (1,090 positive exact-area rows)
    *   `zero_area_row_count`: `3453` within each `run.oracle` (3,453 zero-area rows)
    *   `exception_counts`: `[0, 0]` and `all_oracle_exception_counts_zero: true` (0 exceptions)
    *   `total_exact_areas`: `[26.08321766231042, 26.08321766231042]` (total exact area 26.08321766231042)
    The test `tests/goal3474_shape_pair_exact_overlay_area_shapely_oracle_test.py` also explicitly validates these values.

3.  **Does Goal3475 update the v2.8 gap map honestly, preserving that the real remaining engineering work is a GPU-resident generic simple-polygon overlay-area continuation for nonconvex/high-vertex rows?**
    Yes, Goal3475 updates the v2.8 gap map honestly. The `src/rtdsl/v2_8_benchmark_runtime_gap.py` file, specifically the `current_bottleneck` entry for "Spatial RayJoin," states: "...Goal3474 added a Shapely/GEOS exact CPU oracle... Remaining work is GPU-resident exact overlay-area continuation for non-integer, non-orthogonal, mostly nonconvex polygons...". The `docs/reports/goal3475_v2_8_runtime_gap_after_exact_overlay_oracle_2026-06-05.md` report's "Interpretation" section also clearly states: "The oracle proves the exact area total and row distribution that a future generic GPU simple-polygon overlay-area continuation must reproduce. It also sharpens the remaining gap...". The test `tests/goal3475_v2_8_runtime_gap_after_exact_overlay_oracle_test.py` validates these phrases within the `current_bottleneck`.

4.  **Are release, speedup, RT-core, true-zero-copy, RayJoin reproduction, RTDL-beats-RayJoin, and full overlay-completion claims still blocked?**
    Yes, all these claims remain explicitly blocked. The `_claim_boundary` function in the script `scripts/goal3474_shape_pair_exact_overlay_area_shapely_oracle.py` sets all related flags to `False`. Both `docs/reports/goal3474_shape_pair_exact_overlay_area_shapely_oracle_2026-06-05.md` and `docs/reports/goal3475_v2_8_runtime_gap_after_exact_overlay_oracle_2026-06-05.md` reports contain a "Boundary" section explicitly stating that these claims are *not* authorized. Furthermore, the `src/rtdsl/v2_8_benchmark_runtime_gap.py` defines `V2_8_CLAIM_BOUNDARY` and the `V28BenchmarkRuntimeGapRow` dataclass explicitly prevents these fields from being `True`. The tests `tests/goal3474_shape_pair_exact_overlay_area_shapely_oracle_test.py` and `tests/goal3475_v2_8_runtime_gap_after_exact_overlay_oracle_test.py` verify that these claim flags remain `False` in the generated artifacts and the gap map.

5.  **Are there any correctness risks in the oracle policy, especially Shapely `make_valid` repair, row-order stability, or copying only ordinal columns?**
    Based on the review, the risks appear to be acceptably mitigated or understood within the context of an *oracle*.
    *   **Shapely `make_valid` repair**: The script actively uses `make_valid` (or `buffer(0)` as a fallback) to handle invalid geometries, and the `docs/reports/goal3474_shape_pair_exact_overlay_area_shapely_oracle_2026-06-05.md` report provides "Geometry validity/repair counts," indicating transparency in its use. This repair mechanism is appropriate for an oracle aiming for correctness.
    *   **Row-order stability**: The `goal3474_shape_pair_exact_overlay_area_shapely_oracle_pod_2026-06-05.json` artifact includes `all_row_counts_stable: true` and `all_total_exact_areas_stable: true`, which implies that row processing and resulting area calculations are stable across iterations, addressing concerns about order.
    *   **Copying only ordinal columns**: The script explicitly copies `ordinal` columns (`left_ordinals`, `right_ordinals`) from the GPU to the CPU (`cp.asnumpy`) for use by the Shapely oracle. This is an explicit design choice, and the `docs/reports/goal3475_v2_8_runtime_gap_after_exact_overlay_oracle_2026-06-05.md` report mentions "copies only the generic zero-based ordinal columns to host." The tests confirm that the gap map entry for `spatial_rayjoin` acknowledges the use of these ordinals. This approach is consistent with the oracle's role of validating the results of the RTDL relation stream. The "Interpretation" sections consistently highlight that this is a *correctness target* for a future *GPU continuation*, not a runtime path for RTDL itself.

## Required Verdict

`accept`