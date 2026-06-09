# Gemini Review - Goal4116-4118 RT-DBSCAN Tuned Direct Status

**Date:** 2026-06-09
**Reviewer:** Gemini CLI
**Verdict:** `accept-with-boundary`

---

## Scope

This review covers the Goal4116-4118 RT-DBSCAN chain, focusing on the exposure of `partition_cell_factor` as an explicit user control, its impact on performance, and the resulting updates to route guidance. The deliverables reviewed include:

- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `tests/goal4116_rt_dbscan_explicit_partition_cell_factor_test.py`
- `scripts/goal4117_partition_cell_factor_route_sweep.py`
- `docs/reports/goal4117_partition_cell_factor_route_sweep_2026-06-09.md`
- `docs/reports/goal4117_partition_cell_factor_route_sweep_pod.json`
- `tests/goal4117_partition_cell_factor_route_sweep_test.py`
- `src/rtdsl/current_benchmark_route_decisions.py`
- `docs/reports/goal4118_current_route_decision_after_tuned_direct_status_2026-06-09.md`
- `tests/goal4118_current_route_decision_after_tuned_direct_status_test.py`
- Relevant prior context from Goals 4114, 4115, 4111, and 4112.

---

## Questions Answered

### 1. Does Goal4116 expose `partition_cell_factor` as an explicit user-selected control, without hidden dispatch or automatic tuning?

**Answer:** Yes, Goal4116 exposes `partition_cell_factor` as an explicit user-selected control. The application code (`rtdl_rt_dbscan_benchmark_app.py`) defines it as a direct parameter, and its validity is checked with explicit error handling. Tests (`goal4116_rt_dbscan_explicit_partition_cell_factor_test.py`) explicitly confirm its presence, assert the absence of any auto-tuning or hidden dispatch mechanisms, and verify that user selections are faithfully reflected in metadata. The `claim_boundary` statements across related artifacts further reinforce this explicit, non-automatic nature.

### 2. Does Goal4117 fairly compare the explicit prepared direct-status route against the current grouped-stream Numba route for the same repeated component-signature contract?

**Answer:** Yes, Goal4117 fairly compares the explicit prepared direct-status route against the current grouped-stream Numba route for the same repeated component-signature contract. The comparison is conducted using identical input parameters (dataset, point count, seed, repeat, warmup) for both routes within the sweep script (`goal4117_partition_cell_factor_route_sweep.py`). Crucially, both the script and its tests (`goal4117_partition_cell_factor_route_sweep_test.py`) verify that all tested `partition_cell_factor` values for the direct-status route produce component-size signatures identical to the established current route, ensuring a fair, same-contract comparison.

### 3. Are the key Goal4117 measured results correctly stated?

**Answer:** Yes, the key Goal4117 measured results are correctly stated as requested:
- `clustered3d`: factor `0.25`, replay speedup `2.961x`
- `road3d`: factor `0.25`, replay speedup `1.866x`
- `ngsim_dense`: factor `0.5`, replay speedup `1.312x`
These values align perfectly with the "Result" section of `docs/reports/goal4117_partition_cell_factor_route_sweep_2026-06-09.md`.

### 4. Does the `ngsim_dense` interpretation hold: the Goal4114 loss was caused by the tested default partition granularity, and the larger explicit factor repairs it while preserving signature equality?

**Answer:** Yes, the `ngsim_dense` interpretation holds. The "Interpretation" section of `docs/reports/goal4117_partition_cell_factor_route_sweep_2026-06-09.md` explicitly states that the previous performance regression for `ngsim_dense` (observed in Goal4114 at `0.178x` replay speedup with a `0.125` factor) was due to an inappropriate default partition granularity. By selecting a `0.5` `partition_cell_factor`, the direct-status route now achieves a `1.312x` replay speedup for `ngsim_dense`, repairing the loss while preserving the component-size signature. Tests in `goal4117_partition_cell_factor_route_sweep_test.py` corroborate this by comparing speedups, partition counts, and neighbor offsets.

### 5. Does Goal4118 correctly change RT-DBSCAN route guidance to `mixed_explicit_user_choice` without authorizing automatic factor selection or universal default promotion?

**Answer:** Yes, Goal4118 correctly changes the RT-DBSCAN route guidance to `mixed_explicit_user_choice`. The updated `src/rtdsl/current_benchmark_route_decisions.py` clearly designates the `rt_dbscan` app with `decision_kind="mixed_explicit"` and `partner_policy="mixed_explicit_user_choice"`. The `user_choice_guidance` explicitly instructs users to select the `partition_cell_factor` based on tested evidence and states, "Do not auto-select the factor." Furthermore, the `rejected_or_unpromoted_candidates` list includes `"automatic partition-cell-factor tuning after Goal4117 explicit factor sweep"`, and structural validations (`__post_init__` in `CurrentBenchmarkRouteDecision`) prevent any unauthorized automatic selection or promotion.

### 6. Are all claim boundaries intact: no release, public speedup, broad RT-core, whole-app, paper-reproduction, true-zero-copy, hidden-dispatch, automatic partner selection, automatic factor selection, native ABI, app-specific engine logic, or AMD performance claims?

**Answer:** Yes, all claim boundaries are intact across all reviewed deliverables. Consistent throughout the code, tests, and documentation (e.g., `goal4117_partition_cell_factor_route_sweep.py`, `goal4117_partition_cell_factor_route_sweep_pod.json`, `current_benchmark_route_decisions.py`, and corresponding reports), all authorization flags (e.g., `release_authorized`, `public_speedup_claim_authorized`, `automatic_partner_selection_authorized`) are set to `False`. Explicit statements in `claim_boundary` fields and the `CurrentBenchmarkRouteDecision` dataclass's structural checks (which raise errors if these flags are `True`) collectively prevent any unauthorized claims.

### 7. Are there correctness, determinism, app-agnostic, or performance-risk issues that should block the next engineering step?

**Answer:** No, there are no identified correctness, determinism, app-agnostic, or performance-risk issues that should block the next engineering step.
*   **Correctness and Determinism:** The work explicitly verifies signature equality across different execution paths and factors, and uses fixed seeds for point generation, ensuring deterministic and correct behavior.
*   **App-agnosticism:** The `partition_cell_factor` remains an explicit user control, maintaining app-agnostic principles.
*   **Performance-risk:** While suboptimal factor selection by the user could lead to performance degradation, this risk is acknowledged in the route guidance and is slated for mitigation by a planned "user-visible profile/reuse advisor" (as per Goal4118's `next_runtime_action`). This indicates a recognized and actionable path forward for managing this risk, rather than it being a technical blocker.

---

## Summary

The Goal4116-4118 chain successfully addresses the `ngsim_dense` performance regression observed in Goal4114 by introducing `partition_cell_factor` as an explicit user-selected control. This allows for tuning the direct-status route for different profiles, achieving significant speedups while maintaining correctness and signature equality. The updated route guidance (`current_benchmark_route_decisions.py`) clearly defines a `mixed_explicit_user_choice` policy for RT-DBSCAN, distinguishing between one-shot (grouped-stream Numba) and repeated (tuned direct-status CuPy) workloads. All established claim boundaries are strictly enforced throughout the code, tests, and documentation. No blocking issues were identified, and the path for future work, particularly a user-facing advisor for factor selection, is well-defined.
