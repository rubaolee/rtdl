# Independent Gemini Review: Goals4155-4159 RT-DBSCAN Predicate Direct-Status Chain

Date: 2026-06-09

Verdict: accept-with-boundary

## Reviewed Documents and Source Changes:

- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `docs/reports/goal4155_predicate_aware_direct_status_implementation_plan_2026-06-09.md`
- `docs/reports/goal4156_predicate_direct_status_candidate_surface_2026-06-09.md`
- `docs/reports/goal4157_predicate_direct_status_scale_probe_2026-06-09.md`
- `docs/reports/goal4157_predicate_direct_status_scale_factor025_pod.json`
- `docs/reports/goal4158_predicate_all_true_fast_path_pod_result_2026-06-09.md`
- `docs/reports/goal4158_predicate_all_true_fast_path_scale_factor025_pod.json`
- `docs/reports/goal4159_mixed_predicate_direct_status_gap_2026-06-09.md`
- `docs/reports/goal4159_mixed_predicate_direct_status_scale_pod.json`
- Tests:
    - `tests/goal4155_predicate_aware_direct_status_implementation_plan_test.py`
    - `tests/goal4156_predicate_direct_status_candidate_surface_test.py`
    - `tests/goal4157_predicate_direct_status_scale_probe_test.py`
    - `tests/goal4158_predicate_all_true_fast_path_pod_result_test.py`
    - `tests/goal4159_mixed_predicate_direct_status_gap_test.py`

## Review Answers:

### 1. Is the native/runtime surface still app-agnostic? The route should expose generic predicate flags, fixed-radius component signatures, and explicit policies only; it must not smuggle DBSCAN-specific native logic into the engine.

Yes, the native/runtime surface appears to remain app-agnostic. The documentation (Goals 4155, 4156) explicitly forbids DBSCAN-specific terms (`dbscan`, `cluster`, `core`, `border`, `noise`) in the native ABI. The exposed interface in `v2_8_fixed_radius_graph_component_front_door.py` and the reports adhere to generic predicate flags, fixed-radius component signatures, and explicit policies, avoiding the smuggling of DBSCAN-specific native logic into the engine. The component signature policies are described in generic terms, reinforcing this app-agnostic approach.

### 2. Does Goal4158 genuinely prove the all-predicate fast path after the placement fix at commit `b1d220ed`, with artifact commit `b1d220ed` and report commit chain ending at `63cfbc9a`?

Yes, Goal4158 genuinely proves the all-predicate fast path after the placement fix at commit `b1d220ed`. The report `goal4158_predicate_all_true_fast_path_pod_result_2026-06-09.md` explicitly references the commit `b1d220ed` and the artifact `goal4158_predicate_all_true_fast_path_scale_factor025_pod.json`. Both the report and the JSON data confirm that for all 18 tested scenarios where predicates were all true, the fast path was engaged (`candidate_all_predicate_fast_path: true`), border-candidate work was successfully avoided (`candidate_border_candidate_updates: 0`), and signature parity with the current grouped-stream Numba route was maintained.

### 3. Does Goal4159 correctly classify the mixed-predicate state as a blocked promotion, separating component-label permutation from a real border-assignment policy gap?

Yes, Goal4159 correctly classifies the mixed-predicate state as a blocked promotion. The report `goal4159_mixed_predicate_direct_status_gap_2026-06-09.md` clearly differentiates between "component label-order drift" (where exact labels differ but canonical size signatures match) and a "real border-assignment policy gap" (where even canonical size signatures differ). This distinction is supported by the results table, which shows `Exact signature: no` but `Canonical size signature: yes` for clustered rows, and both `Exact signature: no` and `Canonical size signature: no` for the `road_sparse_many_noise` dataset, confirming a genuine policy discrepancy. The report correctly attributes this to differing border-assignment policies.

### 4. Are the claim boundaries intact? No route promotion, release, public speedup, broad RT-core, whole-app, zero-copy, or hidden-dispatch claim should be authorized.

Yes, the claim boundaries are intact across all reviewed documents and the source code. Every report (Goals 4155 through 4159) explicitly states that route promotion, release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper reproduction, hidden dispatch, automatic partner selection, automatic convergence-mode selection, app-specific engine logic, AMD claims, or true-zero-copy claims are *not* authorized. The `claim_boundary` flags within the JSON artifacts and the `V28FixedRadiusGraphComponentPlan` in the source file consistently set these to `false`.

### 5. What is the next engineering recommendation: canonical component-size signature, explicit generic border-assignment policy, route selector with explicit user opt-in, or another path?

The primary next engineering recommendation, stemming from Goal4159, is to add a **generic border-assignment contract for predicate component signatures**. This contract should expose explicit policies such as `lowest_neighbor`, `lowest_component_root`, or `reference_grouped_stream_compatible`. Additionally, the benchmarks should evolve to compare **canonical component-size signatures** when exact label IDs are not semantically meaningful. This will also help inform whether a second fast path is needed for sparse predicate-true cases, building on the success of the all-predicate fast path from Goal4158, and further reduce unnecessary border-candidate work as noted in Goal4157.