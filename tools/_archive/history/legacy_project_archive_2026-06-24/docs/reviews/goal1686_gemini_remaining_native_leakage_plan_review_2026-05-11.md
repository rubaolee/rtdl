# Gemini Independent Plan/Audit: Remaining Native App Leakage (Goal 1686)

**Date:** 2026-05-11
**Reviewer:** Gemini / Antigravity (Independent External AI)

*Note: This is an independent Gemini/Antigravity static review and integrity audit. This is NOT a Codex review, and no Codex authoring or pair review is treated as valid consensus here.*

## 1. Verdict

The current codebase state accurately reflects the post-Goal1682 migration gap. Source files are structurally intact with no signs of truncation or mount-sync failures. The strategy to systematically migrate the remaining domain-specific native APIs to generic spatial/reduction primitives is technically sound and approved. However, full release readiness remains strictly blocked.

## 2. Count Check

The expected remaining app-shaped native callable/export symbols align perfectly with the current source scan:
- **Total Remaining:** 83
  - `db`: 30
  - `polygon`: 29
  - `knn`: 14
  - `bfs`: 10

The verification suite (`tests.goal1680_current_native_app_leakage_gap_test`, `tests.goal1681_pip_to_point_primitive_anyhit_native_migration_test`, `tests.goal1682_hausdorff_to_max_distance_nearest_candidate_native_migration_test`) passes cleanly, confirming the delta counts match the expected state.

## 3. Source Integrity Check

An integrity check was performed on the recently touched files to detect any mount-sync or truncation fallout:
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/embree_runtime.py`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_workloads.cpp`

**Result:** Clean. Python modules (`src/rtdsl/optix_runtime.py`, `src/rtdsl/embree_runtime.py`, `src/rtdsl/__init__.py`) successfully compile (`py_compile`) with no syntax errors. C++ headers and implementation files show complete, well-formed endings with no truncation or conflict markers.

## 4. Recommended Migration Order

To safely eliminate the remaining 83 leaked symbols while minimizing disruption, the following migration order is recommended:

1. **`bfs`** (10 symbols) - The simplest target; graph expansion naturally maps to generic ray/primitive candidate collection.
2. **`knn`** (14 symbols) - Maps cleanly to K-closest hits or K-nearest bounded candidate collection.
3. **`polygon`** (29 symbols) - A larger surface area but conceptually straightforward replacement with generic geometric intersection and bounded shape collection.
4. **`db`** (30 symbols) - The most complex due to conjunctive scans and table metadata operations; should be handled last as it requires the heaviest reliance on partner tensor lowering and generic grouped reductions.

## 5. Per-Family Plan

### Family: `bfs`
- **Likely Generic Replacement Terminology:** `frontier_expansion`, `edge_primitive_anyhit`, `grouped_candidate_collection`.
- **Files Likely Affected:** `src/native/*/rtdl_*_api.cpp`, `rtdl_*_prelude.h`, graph workload implementation files (`.cu`, `.cpp`, `.mm`).
- **Risks to Python Compatibility:** Low. Python already wraps the BFS logic and can lower graph requests into generic candidate queries.
- **Tests to Update/Add:** `tests/test_bfs*.py`, `tests/test_graph*.py`. Ensure traversal order and depth counts match the original app-shaped behavior.
- **Pod Validation:** Can wait. Batch this validation with `knn` once both are migrated.

### Family: `knn`
- **Likely Generic Replacement Terminology:** `bounded_nearest_k_candidates`, `k_closest_hits`.
- **Files Likely Affected:** `src/native/*/rtdl_*_api.cpp`, `rtdl_*_prelude.h`, `rtdl_*_workloads.cpp`, `src/rtdsl/knn_*.py`.
- **Risks to Python Compatibility:** Medium. Care must be taken to ensure exact K responses and tie-breaking behavior (if any) remain perfectly consistent with the domain-specific legacy APIs.
- **Tests to Update/Add:** `tests/test_knn*.py`.
- **Pod Validation:** Can wait until `polygon` is also migrated.

### Family: `polygon`
- **Likely Generic Replacement Terminology:** `geometric_candidate_intersection`, `bounded_shape_collection`.
- **Files Likely Affected:** All backend APIs (`rtdl_*_api.cpp`), prelude headers, and polygon workload files.
- **Risks to Python Compatibility:** Medium. The Python layer must handle the lowering of complex GIS/polygon semantics into spatial queries while retaining exact edge-case (point-on-edge, degenerate polygon) accuracy.
- **Tests to Update/Add:** `tests/test_polygon*.py`, `tests/test_pip*.py` (for any remaining downstream dependencies).
- **Pod Validation:** Required immediately after this step. The shift in geometric intersection logic must be hardware-proven to guarantee no spatial accuracy degradation.

### Family: `db`
- **Likely Generic Replacement Terminology:** `grouped_scalar_reduction`, `masked_sum`, `filtered_candidate_count`.
- **Files Likely Affected:** Extensive across all backends; involves removing custom table data structures and conjunctive scan kernels.
- **Risks to Python Compatibility:** High. This requires entirely decoupling complex conjunctive scan logic from the engine and shifting it to generic primitive filters or partner tensor evaluation (e.g., PyTorch/CuPy).
- **Tests to Update/Add:** `tests/test_db*.py`, `tests/test_dataset*.py`.
- **Pod Validation:** Mandatory immediately upon completion before any final release claim can be authorized.

## 6. Release Boundary

Release wording claiming that "RTDL native internals are fully app-agnostic" remains **STRICTLY BLOCKED**. No release readiness can or should be claimed. 

The v1.8/v2.0 app-agnostic release gate will remain closed until the 83 leaked symbols are verified to be zero, or any remaining legacy app-shaped surfaces are mechanically quarantined outside the public release surface.
