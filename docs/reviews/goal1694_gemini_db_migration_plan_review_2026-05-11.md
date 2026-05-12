# Gemini Independent Plan/Audit: Goal 1694 DB Migration

**Date:** 2026-05-11
**Reviewer:** Gemini / Antigravity (Independent External AI)

## 1. Post-Goal 1690 Baseline Confirmation
The `bfs` native leakage family was previously successfully fully eliminated. The strict baseline maintains 82 unique symbols, 159 occurrences, and 73 remaining app-shaped families. This baseline cleanly restricts the remaining app-specific terminology to `db` (30), `polygon` (29), and `knn` (14).

## 2. Enumeration of 30 `db` Native Symbols
The strict lowercase regex correctly surfaces 30 actual exported `db` symbols. These must be migrated. Separately, the uppercase `RTDL_DB_*` constant tokens (such as `RTDL_DB_INT32`, `RTDL_DB_FLOAT32`) are known false positives that purely define primitive data types and do not export runtime C ABI endpoints, therefore they do not fail the strict callable app-agnostic audit.

**The 30 true C ABI symbols across backends:**
- **Embree (6):** `rtdl_embree_db_dataset_create`, `rtdl_embree_db_dataset_create_columnar`, `rtdl_embree_db_dataset_destroy`, `rtdl_embree_db_dataset_grouped_sum`, `rtdl_embree_db_dataset_grouped_count`, `rtdl_embree_db_dataset_conjunctive_scan`
- **HIPRT (4):** `rtdl_hiprt_prepare_db_table`, `rtdl_hiprt_destroy_prepared_db_table`, `rtdl_hiprt_db_match_prepared`, `rtdl_hiprt_db_match`
- **OptiX (11):** `rtdl_optix_db_dataset_create`, `rtdl_optix_db_dataset_create_columnar`, `rtdl_optix_db_dataset_destroy`, `rtdl_optix_db_dataset_grouped_sum`, `rtdl_optix_db_dataset_grouped_count`, `rtdl_optix_db_dataset_conjunctive_scan`, `rtdl_optix_db_dataset_conjunctive_scan_count`, `rtdl_optix_db_get_last_phase_timings`, `rtdl_optix_fill_db_compact_summary_phase`, `rtdl_optix_db_compact_summary_results_destroy`, `rtdl_optix_db_dataset_compact_summary_batch`
- **Vulkan (6):** `rtdl_vulkan_db_dataset_create`, `rtdl_vulkan_db_dataset_create_columnar`, `rtdl_vulkan_db_dataset_destroy`, `rtdl_vulkan_db_dataset_grouped_sum`, `rtdl_vulkan_db_dataset_grouped_count`, `rtdl_vulkan_db_dataset_conjunctive_scan`
- **Apple RT (1):** `rtdl_apple_rt_run_db_conjunctive_scan_numeric_compute`
- **Native Cross-Backend (2):** `rtdl_db_conjunctive_scan`, `rtdl_db_match`

## 3. Proposed Generic Columnar Predicate/Reduction Terminology
To satisfy the app-agnostic mandate, domain-specific `db` (database), `table`, and `dataset` semantics must be replaced with generic data structure and compute terms:
- `db_dataset` or `db_table` → `columnar_payload` or `attribute_payload`
- `db_match` → `predicate_match`
- `db_conjunctive_scan` → `multi_predicate_scan` or `masked_predicate_filter`
- `grouped_sum` / `grouped_count` → `grouped_reduction_sum` / `grouped_reduction_count`

**Examples:**
- `rtdl_embree_db_dataset_conjunctive_scan` → `rtdl_embree_columnar_payload_multi_predicate_scan`
- `rtdl_hiprt_prepare_db_table` → `rtdl_hiprt_prepare_columnar_payload`

## 4. Python Compatibility Risks
- **Highest Risk - Semantic Depth:** The "DB" terminology represents the deepest domain specialization in the engine. It handles complex multi-column predicate filtering and data grouping. Ensuring the arguments align perfectly across Python dictionaries and native structs (like `RtdlDbQuery` or `RtdlDbTable`, if they exist) is critical. Ctypes structural layout must remain completely untouched.
- **Python Wrappers:** The Python layer (e.g. `python_rtdl_app_purity.py`, datasets, scan operators) must retain its user-facing `db` methods so user applications don't crash. 
- **Internal Shader/Kernel Strings:** String leakage in `.comp` files (Vulkan), `.cu` internal namespaces (HIPRT), or embedded Apple Metal strings must be systematically replaced to match the C ABI updates. A missed string will cause dynamic loading crashes during execution.

## 5. Recommended Safe Migration Sequence
For the executing AI (Claude/Codex):
1. **Purity Exemption:** Add the new generic structural stems (e.g., `_columnar_payload`, `_predicate_scan`, `_grouped_reduction`) to `_GENERIC_NATIVE_SYMBOL_FRAGMENTS` in `python_rtdl_app_purity.py`.
2. **ABI Export Renaming:** Uniformly replace the 30 `db` symbol names across the C/C++ backend headers (`.h`) and implementations (`.cpp`) using the generic mapping. Leave uppercase `RTDL_DB_*` constants alone.
3. **Internal String Scrubbing:** Search exclusively for embedded kernel string tags, filename lookup hints, and variables containing `db_` or `db.` and update them inline to match the new generic names.
4. **Runtime Re-Binding:** Update the matching `ctypes` bindings inside `src/rtdsl/*_runtime.py` to point to the new generic symbols, explicitly maintaining the original Python wrapper signatures.
5. **Validation:** Run the standard database/query unit tests to guarantee columnar logic holds, and `tests.goal1603_v1_6_stable_native_path_app_leakage_audit_test.py` to verify the 30 symbols have been formally eliminated from the strict regex scan.

*No source files were edited in the preparation of this independent audit and planning document.*
