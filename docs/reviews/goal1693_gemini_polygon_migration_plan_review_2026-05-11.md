# Gemini Independent Plan/Audit: Goal 1693 Polygon Migration

**Date:** 2026-05-11
**Reviewer:** Gemini / Antigravity (Independent External AI)

## 1. Post-Goal 1690 Baseline Confirmation
The `bfs` family (including the Apple RT variants) was successfully eliminated in Goal 1690. The strict source scan baseline correctly identifies 82 unique symbols, 159 occurrences, and 73 remaining app-shaped symbols. This baseline correctly restricts the remaining leakage strictly to the `db` (30), `polygon` (29), and `knn` (14) families. 

## 2. Enumeration of 29 `polygon` Symbols
The 29 unique `polygon` symbols spanning six backends (Embree, HIPRT, OptiX, Oracle, Vulkan, and Apple RT) are:
- **Embree:** `rtdl_embree_run_segment_polygon_hitcount`, `rtdl_embree_collect_polygon_pair_candidates_bounded`, `rtdl_embree_run_segment_polygon_anyhit_rows`
- **HIPRT:** `rtdl_hiprt_run_segment_polygon_anyhit_rows`, `rtdl_hiprt_segment_polygon_2d`, `rtdl_hiprt_run_segment_polygon_hitcount`
- **OptiX:** `rtdl_optix_prepare_segment_polygon_hitcount_2d`, `rtdl_optix_destroy_prepared_segment_polygon_hitcount_2d`, `rtdl_optix_prepare_segment_polygon_anyhit_rows_2d`, `rtdl_optix_run_segment_polygon_hitcount`, `rtdl_optix_run_prepared_segment_polygon_anyhit_rows_2d`, `rtdl_optix_destroy_prepared_segment_polygon_anyhit_rows_2d`, `rtdl_optix_run_prepared_segment_polygon_hitcount_2d`, `rtdl_optix_count_prepared_segment_polygon_hitcount_at_least_2d`, `rtdl_optix_aggregate_prepared_segment_polygon_hitcount_2d`, `rtdl_optix_run_segment_polygon_anyhit_rows`, `rtdl_optix_run_segment_polygon_anyhit_rows_native_bounded`, `rtdl_optix_collect_polygon_pair_candidates_bounded`
- **Oracle:** `rtdl_oracle_run_polygon_pair_overlap_area_rows`, `rtdl_oracle_run_segment_polygon_hitcount`, `rtdl_oracle_run_segment_polygon_anyhit_rows`, `rtdl_oracle_refine_polygon_pair_overlap_area_rows_for_pairs`, `rtdl_oracle_refine_polygon_set_jaccard_for_pairs`, `rtdl_oracle_run_polygon_set_jaccard`
- **Vulkan:** `rtdl_vulkan_run_segment_polygon_anyhit_rows`, `rtdl_vulkan_run_segment_polygon_hitcount`
- **Apple RT:** `rtdl_apple_rt_run_segment_polygon_candidates_2d`, `rtdl_apple_rt_run_point_polygon_candidates_2d`
- **Native Cross-Backend:** `rtdl_native_reduce_polygon_pair_exact_area_summary`

**Files Affected:**
- **Native Interfaces:** `.cpp` and `prelude.h` / `abi.h` exports across all six backends in `src/native/`.
- **Python Runtimes:** `embree_runtime.py`, `hiprt_runtime.py`, `optix_runtime.py`, `oracle_runtime.py`, `vulkan_runtime.py`, and `apple_rt_runtime.py` in `src/rtdsl/`.
- **Purity Validator:** `src/rtdsl/python_rtdl_app_purity.py`.

## 3. Proposed Generic Replacement Terminology
The domain-specific concept of a "polygon" should be translated into generic geometric constructs:
- `segment_polygon` → `segment_shape` or `ray_shape`
- `polygon_pair` → `shape_pair` or `bounded_shape_pair`
- `polygon_set_jaccard` → `shape_set_overlap_ratio`

**Examples:**
- `rtdl_optix_run_segment_polygon_hitcount` → `rtdl_optix_run_segment_shape_hitcount`
- `rtdl_oracle_run_polygon_pair_overlap_area_rows` → `rtdl_oracle_run_shape_pair_overlap_area_rows`

*Any associated ctypes structure names (e.g., `RtdlPolygonRow`) can remain exactly as CamelCase types to preserve structure continuity without violating the strict lowercase ABI purity regex.*

## 4. Python Compatibility Risks
- **GIS Semantic Integrity:** Python's upper layers rely strictly on these functions for complex Geographic Information System (GIS) queries. Changing inner bounds, point-on-edge logic, or geometry winding rules while migrating C-level identifiers could quietly corrupt GIS data results. Logic must remain structurally untouched.
- **Embedded Kernel Strings:** Vulkan `.comp` files, HIPRT `.cu` filename hints, and Apple Metal shader names dynamically loaded via string lookups must be perfectly scrubbed of `polygon`. Inconsistent string replacement here will lead to hard runtime pipeline lookup failures.

## 5. Recommended Safe Migration Sequence
For the executing AI (Claude/Codex):
1. **Purity Exceptions:** Add the newly chosen generic stems (e.g., `_segment_shape`, `_shape_pair`) to `_GENERIC_NATIVE_SYMBOL_FRAGMENTS` within `python_rtdl_app_purity.py`.
2. **ABI Export Renaming:** Apply the generic mapping uniformly across all 29 definitions in the C/C++ backend headers and implementations.
3. **Internal String Scrubbing:** Search exclusively for embedded kernel string tags and filenames containing `polygon` in the backend directories and update them inline to match the new ABI names.
4. **Runtime Re-Binding:** Update the matching ctypes `getattr` bindings in `src/rtdsl/*_runtime.py` to point to the generic `_shape` exports, while explicitly keeping the public Python wrapper signatures unmodified.
5. **Validation:** Run the standard polygon tests (`tests/test_polygon*.py`) to guarantee GIS logic is intact, and the purity test (`tests.goal1603_v1_6_stable_native_path_app_leakage_audit_test.py`) to confirm the count drops precisely by 29.

*No source files were edited in the preparation of this independent audit and planning document.*
