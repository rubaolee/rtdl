# Gemini Review - Goal4107-4110 Prepared Direct Status Chain

Date: 2026-06-09

Verdict: accept-with-boundary

## Review of Goals 4107-4110

This review covers Goals 4107-4110, focusing on the introduction of a prepared direct-status union handle for RT-DBSCAN, its timing characteristics, exposure as an explicit app mode, and the updated route guidance.

### Goal4107: prepared direct-status union handle

**Question 1: Does Goal4107 genuinely prepare reusable point/partition columns without materializing near-pair columns or app-specific native ABI?**

**Answer:** Yes, Goal4107 genuinely prepares reusable point/partition columns without materializing near-pair columns or app-specific native ABI. The code explicitly sets `near_pair_columns_materialized: False`, `partition_pair_rows_materialized: False`, and `pair_materialization_avoided: True` in the metadata of the prepared objects (`V28PreparedFixedRadiusPartitionConvergenceDirectStatusUnionCupyPreview3D`). The tests (`tests/goal4107_prepared_direct_status_union_handle_test.py`) confirm these properties and assert the absence of app-specific terms like "dbscan" or "cluster," ensuring no app-specific native ABI is introduced.

### Goal4108: prepared direct-status reuse timing

**Question 2: Does Goal4108 fairly distinguish prepared replay evidence from one-shot/default-route evidence?**

**Answer:** Yes, Goal4108 fairly distinguishes prepared replay evidence from one-shot/default-route evidence. The timing script (`scripts/goal4108_prepared_direct_status_reuse_timing.py`) meticulously measures preparation time, prepared replay time (multiple runs after one preparation), one-shot direct status time, and current default route time. The accompanying report (`docs/reports/goal4108_prepared_direct_status_reuse_timing_2026-06-09.md`) and JSON artifact (`docs/reports/goal4108_prepared_direct_status_reuse_timing_pod.json`) clearly present these distinct measurements and performance comparisons (speedup ratios). The metadata explicitly tracks whether the handle is used and reused, confirming the distinction.

### Goal4109: explicit RT-DBSCAN app mode

**Question 3: Does Goal4109 expose a clear user-facing app mode while preserving the graph-component-only and non-default-route boundary?**

**Answer:** Yes, Goal4109 exposes a clear user-facing app mode (`partner_cupy_prepared_direct_status_union_component_signature_3d`) while preserving the graph-component-only and non-default-route boundary. The benchmark application (`examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`) includes this new mode, and the associated reports and artifacts consistently indicate `prepared_direct_status_union_app_mode: true`, `graph_component_contract_only: true`, `full_dbscan_semantics: false`, and `current_default_route: false`. The `claim_boundary` further reinforces these limitations, and tests prevent the materialization of Python rows, upholding the "column-signature only" aspect.

### Goal4110: current route guidance refresh

**Question 4: Does Goal4110 correctly keep one-shot RT-DBSCAN guidance conservative while allowing explicit prepared direct-status use for repeated component-signature workloads?**

**Answer:** Yes, Goal4110 correctly keeps one-shot RT-DBSCAN guidance conservative while allowing explicit prepared direct-status use for repeated component-signature workloads. The updated `src/rtdsl/current_benchmark_route_decisions.py` provides split guidance: the existing RTDL/OptiX grouped stream with Numba continuation for one-shot, and the explicit CuPy prepared direct-status app mode for workloads reusing point/partition columns. The `rejected_or_unpromoted_candidates` and `next_runtime_action` clearly indicate that universal default promotion for the new path is blocked, with future work planned to define an explicit reuse threshold. All claim boundaries are strictly maintained.

### General Questions

**Question 5: Are claim boundaries intact: no release, public speedup, broad RT-core, whole-app, paper-reproduction, true-zero-copy, hidden-dispatch, automatic-partner-selection, native-ABI, or app-specific-engine claims?**

**Answer:** Yes, the claim boundaries are intact. All reviewed files (code, tests, reports, and JSON artifacts) consistently set relevant authorization flags to `false` (e.g., `release_authorized`, `public_speedup_claim_authorized`, `true_zero_copy_claim_authorized`, `automatic_partner_selection_authorized`, `native_abi_added`, `app_specific_engine_logic_allowed`). Reports and claim boundaries explicitly state the avoidance of such claims, including for broad RT-core, whole-app, paper-reproduction, and hidden dispatch.

**Question 6: Are there correctness, determinism, route-guidance, or performance-risk issues that should block the next engineering step?**

**Answer:** No, there are no correctness, determinism, route-guidance, or performance-risk issues identified that should block the next engineering step.
*   **Correctness and Determinism:** Extensive testing and validation against references are in place across the goals, and the point generation uses a fixed seed, implying deterministic behavior.
*   **Route-guidance:** The route guidance is appropriately conservative, clearly distinguishing between one-shot and repeated-use scenarios and avoiding premature universal promotion.
*   **Performance-risk:** The reports openly acknowledge that the new prepared direct-status app mode is "prepare-dominated" for one-shot execution and has a narrower speedup margin for the `ngsim_dense` profile. These limitations are explicitly cited as reasons for conservative promotion, and the `next_runtime_action` outlines future work to quantify reuse benefits and define thresholds. This proactive approach mitigates performance risks.

## Summary

The work across Goals 4107-4110 successfully introduces a prepared direct-status union handle, demonstrates its performance benefits in reuse scenarios, exposes it as an explicit user-facing app mode, and updates the central route guidance to reflect its appropriate use cases (primarily repeated component-signature workloads). All established claim boundaries are rigorously maintained, and potential performance caveats are acknowledged with clear next steps for further investigation.
