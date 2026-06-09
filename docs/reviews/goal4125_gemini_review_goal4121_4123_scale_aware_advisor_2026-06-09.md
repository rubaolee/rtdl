# Independent Gemini Review - Goal4121-4123 RT-DBSCAN Scale-Aware Advisor

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

This review evaluates Goal4121 (RT-DBSCAN Explicit Route Choice Advisor), Goal4122 (Tuned Direct-Status 131k Scale Probe), and Goal4123 (Current Route Decision After Scale-Aware Advisor). The primary objective is to confirm that these goals correctly implement scale-aware route guidance for RT-DBSCAN within defined boundaries, without introducing unauthorized claims or automatic behaviors.

## Questions Answered:

### 1. Does Goal4121's advisor remain advisory-only, with no hidden dispatch, no automatic partner selection, and no automatic factor selection?

**Answer:** **accept**

Goal4121's advisor, implemented through `explain_rt_dbscan_explicit_route_choice` in `rtdl_rt_dbscan_benchmark_app.py`, explicitly indicates its advisory-only nature. The function's output metadata contains `"status": "advisory_only_no_dispatch"`, `"user_must_select_route": True`, and explicitly sets `False` for `automatic_dispatch_authorized`, `automatic_partner_selection_authorized`, `automatic_partition_cell_factor_selection_authorized`, and `hidden_dispatch_allowed`. The accompanying documentation (`docs/reports/goal4121_rt_dbscan_explicit_route_choice_advisor_2026-06-09.md`) and tests (`tests/goal4121_rt_dbscan_explicit_route_choice_advisor_test.py`) consistently reinforce these restrictions, confirming no hidden dispatch or automatic selections.

### 2. Does the advisor correctly expose scale-aware NGSIM evidence: `0.5` at 65k from Goal4117 and `0.25` at 131k from Goal4122?

**Answer:** **accept**

Yes, the advisor correctly exposes this scale-aware evidence. The `RT_DBSCAN_TESTED_DIRECT_STATUS_PARTITION_CELL_FACTOR_OPTIONS` dictionary in `rtdl_rt_dbscan_benchmark_app.py` contains entries for "ngsim_dense" showing `factor: 0.5` at `point_count: 65536` with `evidence_refs: ("Goal4117",)` and `factor: 0.25` at `point_count: 131072` with `evidence_refs: ("Goal4122",)`. The `explain_rt_dbscan_explicit_route_choice` function correctly sorts these options, prioritizing the one closest to the requested `point_count`. This behavior is explicitly validated by the `test_ngsim_scale_aware_options_rank_closest_evidence_first` in `tests/goal4121_rt_dbscan_explicit_route_choice_advisor_test.py`.

### 3. Does Goal4122 fairly reuse the Goal4117 runner for a 131,072-point scale probe, and are the key measured results correctly stated?

**Answer:** **accept**

Yes, Goal4122 fairly reuses the Goal4117 runner. The `goal4122_tuned_direct_status_scale_probe_2026-06-09.md` report explicitly states this reuse, and the `goal4122_tuned_direct_status_scale_probe_pod.json` artifact's schema (`"rtdl.goal4117.partition_cell_factor_route_sweep.v1"`) confirms it. The `point_count` in the artifact is `131072`.

The key measured results are correctly stated:
- `clustered3d`: factor `0.25`, replay speedup `3.211x`
- `road3d`: factor `0.25`, replay speedup `1.545x`
- `ngsim_dense`: factor `0.25`, replay speedup `1.399x`
These values match precisely with the `best_replay_partition_cell_factor` and `best_replay_over_current_speedup` reported in the `goal4122_tuned_direct_status_scale_probe_pod.json` artifact and verified by `tests/goal4122_tuned_direct_status_scale_probe_test.py`.

### 4. Does Goal4123 correctly update current route guidance to scale-aware evidence without claiming a universal dense-profile factor?

**Answer:** **accept**

Yes, Goal4123 correctly updates the route guidance to be scale-aware without claiming a universal dense-profile factor. The `rt_dbscan` entry in `src/rtdsl/current_benchmark_route_decisions.py` explicitly guides users to select `partition_cell_factor` based on tested evidence and scale (e.g., "0.5 at 65k and 0.25 at 131k" for dense NGSIM-like profiles), explicitly stating "Do not auto-select the factor." This is further detailed and reinforced in `docs/reports/goal4123_current_route_decision_after_scale_aware_advisor_2026-06-09.md` and validated by `tests/goal4123_current_route_decision_after_scale_aware_advisor_test.py`.

### 5. Are all claim boundaries intact: no release, public speedup, broad RT-core, whole-app, paper-reproduction, true-zero-copy, hidden-dispatch, automatic partner selection, automatic factor selection, native ABI, app-specific engine logic, or AMD performance claims?

**Answer:** **accept**

All claim boundaries are intact and consistently enforced across the code and documentation. Explicit `False` flags are present in relevant metadata outputs (`release_authorized`, `public_speedup_claim_authorized`, `broad_rt_core_claim_authorized`, `whole_app_speedup_claim_authorized`, `paper_reproduction_claim_authorized`, `true_zero_copy_claim_authorized`, `automatic_partner_selection_authorized`, `automatic_partition_cell_factor_selection_authorized`, `native_abi_added`, `app_specific_engine_logic_allowed`, `amd_performance_claim_authorized`). Narrative documents and `claim_boundary` strings reiterate these restrictions, explicitly stating that such claims are not authorized. The `CurrentBenchmarkRouteDecision` class also includes runtime validation to prevent accidental authorization of these claims.

### 6. Are there correctness, determinism, app-agnostic, or performance-risk issues that should block the next engineering step?

**Answer:** **accept**

No, there are no correctness, determinism, app-agnostic, or performance-risk issues identified that should block the next engineering step.
-   **Correctness:** The logic for advisory route choices, evidence presentation, and route guidance updates is thoroughly tested and appears correct.
-   **Determinism:** Deterministic point generation via seeding is used in benchmarks, and the stability of signatures across repeated runs (as noted in Goal4122's artifact) indicates expected deterministic behavior.
-   **App-agnostic:** The work focuses on providing guidance and evidence for RT-DBSCAN app routes without embedding app-specific logic into the core RTDL engine, preserving app-agnostic principles.
-   **Performance-risk:** While performance optimization is a continuous process, the current work explicitly defines internal boundaries for claims and identifies future work (e.g., "larger representative-scale packet beyond 131k"), indicating a managed approach to performance, not a blocking risk in the current state. The core contribution is explicit guidance, which *mitigates* the risk of suboptimal choices, rather than introducing new performance risks.