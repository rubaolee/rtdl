# Antigravity Review Verdict: Goal5075 RT-BarnesHut Generic Aggregate Force-Output Bridge

**Date:** 2026-07-06
**Verdict:** `approve_goal5075_app_owned_scalar_force_output_bridge`

---

## 1. Summary of Review Findings

We have reviewed the Goal5075 implementation in [goal5075_rt_barneshut_generic_aggregate_force_output_bridge_result_2026-07-06.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal5075_rt_barneshut_generic_aggregate_force_output_bridge_result_2026-07-06.md) against the review scope and target files.

Goal5075 successfully implements the app-owned scalar force-output bridge. It maps generic aggregate reducer rows into the RT-BarnesHut app's scalar force-output rows, preserving the generic system/app boundary. The core RTDL modules remain completely free of Barnes-Hut force semantics, comparative policies, or native hooks. The regression test suite has been successfully extended and runs 64 tests with exact JIT and reference parity (`mismatch_count = 0`).

---

## 2. Answers to Review Questions

### 1. Does the implementation correctly recognize that the app force output is scalar, not a 3D vector?
**Yes.** The author-side force output for this application is scalar. The bridge correctly maps the generic inverse-square scalar reducer JIs (`reducer_value_0`) to scalar force values under the key `"scalar_force"`.

### 2. Is the `0.1` force scale kept in the app adapter rather than promoted into RTDL core?
**Yes.** The `0.1` scaling factor is defined inside the app-owned [aggregate_hierarchy_adapter.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py) as `DEFAULT_FORCE_OUTPUT_SCALE = 0.1`. RTDL core remains entirely agnostic of this scale.

### 3. Does the bridge use public generic RTDL aggregate-hierarchy APIs rather than a torch extension, native OptiX hook, or author payload shortcut?
**Yes.** The bridge invokes the public generic APIs: `rt.aggregate_hierarchy_3d`, `rt.prepare_aggregate_hierarchy_3d`, and `rt.aggregate_frontier_reduce_execution_contract_3d`. It contains no torch/native OptiX imports or private hooks.

### 4. Does the implementation preserve the boundary that RTDL core produces generic reducer rows and the RT-BarnesHut app owns scalar force formatting?
**Yes.** RTDL core produces only generic reducer rows (e.g., `reducer_value_0`), whereas formatting the scalar force text rows (`write_scalar_force_rows`) and translating row keys are handled strictly within the app.

### 5. Do the tests prove that optional Numba output and CPU reference output map to identical scalar force rows on the controlled route?
**Yes.** The test `test_app_owned_force_output_bridge_matches_author_contract_reference` asserts that both reference and Numba output arrays translate to identical scalar force rows with zero mismatch.

### 6. Does the CLI smoke evidence show that the app can write a bounded scalar force file from prepared arrays?
**Yes.** The test `test_aggregate_numba_force_output_mode_writes_scalar_force_file` runs the CLI mode `aggregate-numba-force-output` and asserts that a force output file of 32 rows is successfully materialized.

### 7. Are the claim boundaries correct: not author binary comparator, not paper completion, not performance, not device-resident/native?
**Yes.** The adapters and status models explicitly declare the boundaries: `not_author_binary_comparator`, `not_paper_reproduction_completion`, `not_performance_claim`.

### 8. Do the leak checks sufficiently show that no BarnesHut or RayJoin identity was inserted into `src/rtdsl/aggregate_hierarchy.py`?
**Yes.** The file [src/rtdsl/aggregate_hierarchy.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/aggregate_hierarchy.py) was not modified in this Goal and remains clean of any app identity or RayJoin leaks.

### 9. Is it acceptable that force-file text formatting uses finite decimal output with file-level tolerance, while internal bridge comparison remains exact on the in-memory rows?
**Yes.** Decimal formatting via `:.9g` matches the precision qualities of author dumps, making file-level comparative testing clean, while internal validation operates exactly on float variables to guarantee backend JIT compiler correctness.

### 10. Should the next goal be a bounded same-input scalar force comparator against an author prepared-state plus force dump, still owned by the paper app?
**Yes.** This is the correct next step. The app should setup a comparative gate that consumes the patched-author binary's dumped prepared arrays and force outputs, compares them to the generic adapter bridge outputs, and operates within the paper app to establish final correctness.
