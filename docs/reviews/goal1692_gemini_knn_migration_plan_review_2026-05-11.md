# Gemini Independent Plan/Audit: Goal 1692 KNN Migration

**Date:** 2026-05-11
**Reviewer:** Gemini / Antigravity (Independent External AI)

## 1. Post-Goal 1690 Baseline Confirmation
The `bfs` native leakage family was successfully migrated, and Apple RT deferred targets were resolved. The current codebase sits at 82 unique symbols, 159 occurrences, and 73 remaining app-shaped families. This baseline is clean, verified, and correctly tracks the remaining `db`, `polygon`, and `knn` families.

## 2. Enumeration of 14 `knn` Symbols
The 14 unique `knn` symbols spanning four backends (Embree, OptiX, Oracle, Vulkan) are:
- **Embree (5):** `rtdl_embree_knn_rows_2d_create`, `rtdl_embree_knn_rows_2d_run`, `rtdl_embree_knn_rows_2d_destroy`, `rtdl_embree_run_knn_rows`, `rtdl_embree_run_knn_rows_3d`
- **OptiX (2):** `rtdl_optix_run_knn_rows`, `rtdl_optix_run_knn_rows_3d`
- **Oracle (5):** `rtdl_oracle_run_knn_rows`, `rtdl_oracle_run_knn_rows_3d`, `rtdl_oracle_run_bounded_knn_rows`, `rtdl_oracle_run_bounded_knn_rows_3d`, `rtdl_oracle_summarize_knn_rows`
- **Vulkan (2):** `rtdl_vulkan_run_knn_rows`, `rtdl_vulkan_run_knn_rows_3d`

**Files Affected:** 
- **Native Headers/Impl:** `src/native/embree/rtdl_embree_api.cpp`, `src/native/embree/rtdl_embree_prelude.h`, `src/native/vulkan/rtdl_vulkan_api.cpp`, `src/native/vulkan/rtdl_vulkan_prelude.h`, `src/native/vulkan/rtdl_vulkan_core.cpp`, `src/native/oracle/rtdl_oracle_api.cpp`, `src/native/oracle/rtdl_oracle_abi.h`, `src/native/optix/rtdl_optix_api.cpp`, `src/native/optix/rtdl_optix_prelude.h`.
- **Python Runtimes:** `src/rtdsl/embree_runtime.py`, `src/rtdsl/optix_runtime.py`, `src/rtdsl/oracle_runtime.py`, `src/rtdsl/vulkan_runtime.py`.
- **Purity Config:** `src/rtdsl/python_rtdl_app_purity.py`.

## 3. Proposed Generic Replacement Terminology
To satisfy the app-agnostic mandate, domain-specific `knn` semantics must be replaced with generic spatial terminology:
- Replace `knn_rows` with `k_closest_hits` (or `k_nearest_candidates`).
- Example mappings:
  - `rtdl_embree_run_knn_rows` → `rtdl_embree_run_k_closest_hits`
  - `rtdl_oracle_run_bounded_knn_rows_3d` → `rtdl_oracle_run_bounded_k_closest_hits_3d`

*Note: The CamelCase struct `RtdlKnnNeighborRow` does not trigger the strict `\brtdl_<lowercase>_` regex audit. It can safely remain untouched as a ctypes boundary structure, exactly as was done for `RtdlBfsRow` in previous goals.*

## 4. Python Compatibility Risks
- **Tie-Breaking and Exact K Validation:** The highest risk is accidentally altering exact distance tie-breaking behavior or candidate limits when translating the inner kernel loops. The logic must remain byte-for-byte identical; only the function names should change.
- **Python Wrappers:** The Python domain logic must continue exposing `knn` semantics (e.g., `rt.run_knn_rows()`). Only the internal `ctypes` bindings should be updated to use `k_closest_hits`.
- **String/Kernel Leakage:** Similar to HIPRT in earlier migrations, Vulkan's internal `knn.comp` and `knn3d.comp` shader filename strings and variable names (e.g., `kKnnComp`) must be scrubbed to ensure no hidden string-level leakage remains.

## 5. Recommended Safe Migration Sequence
To ensure a secure transition, the migrating AI (Claude/Codex) should follow this sequence:
1. **Purity Exemption:** Add `_k_closest_hits` to `_GENERIC_NATIVE_SYMBOL_FRAGMENTS` in `python_rtdl_app_purity.py`.
2. **Backend ABI Rename:** Execute the rename of the 14 ABI symbols across the four backend APIs (`.cpp` and `.h`). 
3. **Internal Scrubbing:** Update associated compute shader filenames and string tags in Vulkan and other backends.
4. **Python Bindings:** Update the `_lib.rtdl_*` symbol lookups in the Python runtime modules without altering the outer Python API signatures or behavior.
5. **Validation:** Run `tests.goal1603_v1_6_stable_native_path_app_leakage_audit_test` to verify the 14 symbols are fully eliminated, and execute the standard suite to prove Python compatibility.

*This sequence guarantees a mechanical, non-behavioral migration with no disruption to the Python boundary. No native source files were edited during this independent planning phase.*
