# Independent Gemini Review — Goals 4134–4135: RT-DBSCAN 524k Factor-0.25 Extension

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

This review evaluates Goal4134 (Tuned Direct-Status 524k Factor-0.25 Probe) and Goal4135 (Current Route Decision After 524k Factor-0.25 Probe). The primary objectives are to confirm that the 524k probe is correctly scoped to a single factor, that the artifact is commit-pinned with a clean worktree, that all six reported speedup values are exactly supported by the JSON artifact, that all factor rows preserve the component-size signature, that the advisor correctly handles the one-shot vs. repeated asymmetry (including the 65k ngsim_dense case), that the route registry remains advisory-only with no hidden dispatch or automatic selection, and that all claim boundaries are intact.

Prior context: Goal4117 factor-sweep runner, Goal4122 131k probe, Goal4126 262k probe, Goal4130 one-shot probe, Goal4132 Claude review and Goal4133 Gemini review of Goals 4130–4131.

---

## Questions Answered

### 1. Does Goal4134 fairly run a bounded 524,288-point extension probe with only `partition_cell_factor=0.25`, and is the artifact cleanly commit-pinned to `93c52cb1` with dirty flag false?

**Answer: accept**

The JSON artifact carries `"schema": "rtdl.goal4117.partition_cell_factor_route_sweep.v1"`, the same schema used by the Goal4117, Goal4122, Goal4126, and Goal4130 pod family. The `"partition_cell_factors"` array is `[0.25]` — a single entry confirming this is a bounded single-factor extension and not a full factor sweep.

Commit pinning: `"source_commit": "93c52cb1e316dd30046cf3cd393102edad479a95"` with `"source_tracked_worktree_dirty": false`. `"point_count": 524288`, `"repeat": 2`, `"warmup": 1` — consistent with the one-shot-compatible measurement protocol from Goal4130.

The test `test_artifact_is_clean_commit_pinned_and_non_authorizing` verifies the schema, commit prefix `93c52cb1`, clean-worktree flag, `point_count == 524288`, `partition_cell_factors == [0.25]`, and all five authorization flags as `false`. ✓

The `"goal": "Goal4117"` top-level field is a schema-provenance identifier, not a measurement-goal label. This is the established convention for this pod family, confirmed in the Goal4133 review. ✓

---

### 2. Are the reported 524k replay and one-shot total speedups exactly supported by the JSON artifact?

**Answer: accept**

The replay speedup for each profile is `current_route_replay_sec / factor_rows[0]["replay_sec"]`. The one-shot total speedup is `current_route_amortized_sec / factor_rows[0]["amortized_sec"]`, where `amortized_sec = prepare_sec + replay_sec` and `current_route_amortized_sec = current_route_prepare_sec + current_route_replay_sec`.

**Arithmetic verification:**

clustered3d:
- Current prepare + replay: `2.4557399600744247 + 5.063082933425903 = 7.518822893500328` = JSON `current_route_amortized_sec` ✓
- Direct prepare + replay: `0.7747924253344536 + 1.538508579134941 ≈ 2.313301004` = JSON `amortized_sec` 2.3133010044693947 ✓
- Replay speedup: `5.063082933425903 / 1.538508579134941 = 3.29090...` → JSON `best_replay_over_current_speedup` = 3.2909032826276006. Report: `3.291x`. ✓
- One-shot speedup: `7.518822893500328 / 2.3133010044693947 = 3.25026...` → JSON `amortized_over_current_speedup` = 3.2502570478176627. Report: `3.250x`. ✓

road3d:
- Current prepare + replay: `1.468694843351841 + 1.8349839448928833 = 3.3036787882447243` = JSON `current_route_amortized_sec` ✓
- Direct prepare + replay: `0.38805846869945526 + 1.342011235654354 ≈ 1.73007` = JSON `amortized_sec` 1.7300697043538094 ✓
- Replay speedup: `1.8349839448928833 / 1.342011235654354 = 1.36734...` → JSON = 1.367338734685153. Report: `1.367x`. ✓
- One-shot speedup: `3.3036787882447243 / 1.7300697043538094 = 1.90956...` → JSON = 1.909563978798569. Report: `1.910x`. ✓

ngsim_dense:
- Current prepare + replay: `1.4040890857577324 + 0.5969996601343155 = 2.001088745892048` = JSON `current_route_amortized_sec` ✓
- Direct prepare + replay: `0.4663591608405113 + 0.3375139683485031 = 0.8038731291890144` = JSON `amortized_sec` ✓
- Replay speedup: `0.5969996601343155 / 0.3375139683485031 = 1.76881...` → JSON = 1.7688146747096347. Report: `1.769x`. ✓
- One-shot speedup: `2.001088745892048 / 0.8038731291890144 = 2.48931...` → JSON = 2.489309162393376. Report: `2.489x`. ✓

All six values match the JSON raw fields and arithmetic cross-checks to three decimal places. The test `test_factor025_stays_positive_at_524k` asserts conservative lower bounds — `minimum_replay` of `{"clustered3d": 3.2, "road3d": 1.3, "ngsim_dense": 1.7}` and `minimum_one_shot` of `{"clustered3d": 3.2, "road3d": 1.9, "ngsim_dense": 2.4}` — all satisfied by the JSON values. ✓

---

### 3. Do all factor rows preserve the current grouped-stream route's component-size signature?

**Answer: accept**

All three profile rows in the JSON carry `"same_signature": true` on their single factor-row entry (the only factor tested is 0.25). All three per-profile rows carry `"all_factors_match_current_signature": true`. There are no sub-parity replay entries: all three profiles are above 1.0x replay speedup at 524k with factor 0.25.

The test `test_factor025_stays_positive_at_524k` asserts `assertTrue(factor["same_signature"])` and `assertTrue(row["all_factors_match_current_signature"])` for all three profiles. ✓

---

### 4. Does Goal4135 correctly state that the 524k packet is a factor-0.25 extension, not a full 524k factor sweep or universal factor claim?

**Answer: accept**

The Goal4135 report states: "The 524k packet does not run a full factor sweep. It only confirms that factor `0.25` remains above parity at the larger scale for the three tested profiles."

The `rejected_or_unpromoted_candidates` tuple in `current_benchmark_route_decisions.py` explicitly includes:

```python
"universal factor sweep claim after Goal4134 factor-0.25-only 524k extension"
```

The Goal4134 report's boundary section states: "Because this probe tests only factor `0.25`, it does not authorize a full 524k factor ranking or a universal factor claim. It only extends the advisory evidence table for the currently winning factor."

The test `test_route_registry_records_limited_524k_extension` asserts `assertIn("factor-0.25-only", " ".join(route["rejected_or_unpromoted_candidates"]))`. ✓

---

### 5. Does the advisor correctly distinguish repeated replay ranking from one-shot total ranking, especially the 65k `ngsim_dense` asymmetry (`0.5` for repeated replay, `0.25` for one-shot total)?

**Answer: accept**

`explain_rt_dbscan_explicit_route_choice` (benchmark app lines 134–144) assigns:

```python
metric_key = "replay_speedup" if repeated else "one_shot_total_speedup"
```

and sorts by `(distance_from_point_count, -metric_key_value, factor)`.

For `ngsim_dense` at `point_count=65536`, two entries exist with equal distance (zero):

| Factor | replay_speedup | one_shot_total_speedup |
|---|---|---|
| 0.25 | 0.969 | 3.679 |
| 0.5 | 1.312 | 1.819 |

With `repeated=False` (one-shot): secondary key is `-one_shot_total_speedup`. Factor 0.25 scores −3.679 vs. factor 0.5 at −1.819; factor 0.25 ranks first (smaller secondary key). ✓
With `repeated=True` (replay): secondary key is `-replay_speedup`. Factor 0.5 scores −1.312 vs. factor 0.25 at −0.969; factor 0.5 ranks first. ✓

The asymmetry is explicitly documented in `user_choice_guidance`: "For dense NGSIM-like profiles, use the route advisor because the 65k best factor depends on intent: one-shot total timing ranks 0.25 first, while repeated replay ranks 0.5 first; 131k/262k/524k rank 0.25 first for the tested evidence."

The test `test_advisor_ranks_524k_evidence_first_without_dispatch` verifies that for `road3d`, `point_count=524288`, `repeated_component_signature=False`, the first option has `tested_point_count == 524288`, `partition_cell_factor == 0.25`, `replay_speedup_vs_current > 1.3`, `one_shot_total_speedup_vs_current > 1.9`, and `"Goal4134"` in `evidence_refs`. ✓

The 524k ngsim_dense entry has only one factor (0.25), so there is no ambiguity at the new scale. ✓

---

### 6. Does the current route registry remain advisory-only, with no hidden dispatch, automatic route selection, automatic partner selection, or automatic factor selection?

**Answer: accept**

`explain_rt_dbscan_explicit_route_choice` (benchmark app lines 174–199) returns the full set of advisory enforcement flags:

- `"status": "advisory_only_no_dispatch"` ✓
- `"user_must_select_route": True` ✓
- `"automatic_dispatch_authorized": False` ✓
- `"automatic_partner_selection_authorized": False` ✓
- `"automatic_partition_cell_factor_selection_authorized": False` ✓
- `"hidden_dispatch_allowed": False` ✓

The function does not call `run_rt_dbscan_benchmark` or any route executor. The sort of `tested_options` by nearest scale and metric is purely informational.

`CurrentBenchmarkRouteDecision.__post_init__` (registry lines 67–100) enforces all nine authorization flags as `False` and `user_explicit_choice_required` as `True` at construction time, making it structurally impossible to serialize a registry entry with any prohibited flag set.

The test `test_advisor_ranks_524k_evidence_first_without_dispatch` asserts all three automatic-selection flags are `False`. The test `test_registry_summary_and_report_stay_non_authorizing` asserts `validate_current_benchmark_route_decisions()` returns `status="accept"` with `errors == ()`, and that `summarize_current_benchmark_route_decisions()` returns all authorization flags as `False`. ✓

`plan_rt_dbscan_execution` (benchmark app lines 81–107) remains unchanged — it uses Goal2425 evidence, returns `"not_hidden_dispatcher": True`, and does not reference the Goal4134 524k data. The two planning surfaces remain structurally separate. ✓

---

### 7. Are all claim boundaries intact: no release, public speedup, broad RT-core, whole-app, paper reproduction, true-zero-copy, hidden dispatch, automatic partner selection, automatic factor selection, native ABI, app-specific engine logic, or AMD performance claims?

**Answer: accept**

All prohibited claim flags are `False` across all surfaces.

In the JSON pod: `release_authorized`, `public_speedup_claim_authorized`, `rt_core_speedup_claim_authorized`, `whole_app_speedup_claim_authorized`, `automatic_partner_selection_authorized`, `native_abi_added`, `app_specific_engine_logic_allowed`, `partition_convergence_hybrid_promoted`, and `true_zero_copy_claim_authorized` are `false` at the top level, at the per-profile level, and inside every factor-row entry.

In the advisor packet: all twelve advisory enforcement flags (`release_authorized`, `public_speedup_claim_authorized`, `broad_rt_core_claim_authorized`, `whole_app_speedup_claim_authorized`, `true_zero_copy_claim_authorized`, `native_dbscan_abi_added`, `app_specific_engine_logic_allowed`, `automatic_dispatch_authorized`, `automatic_partner_selection_authorized`, `automatic_partition_cell_factor_selection_authorized`, `hidden_dispatch_allowed`) are `False` (benchmark app lines 184–191).

In the route registry: the `CurrentBenchmarkRouteDecision` dataclass enforces all nine authorization flags at construction time via `__post_init__`. `validate_current_benchmark_route_decisions()` returns `status="accept"` with `errors == ()`.

The `CURRENT_BENCHMARK_ROUTE_DECISION_CLAIM_BOUNDARY` string now enumerates "a 524k factor-0.25 extension probe" in the evidence chain and lists all prohibited actions. The `rt_dbscan` registry entry's `rejected_or_unpromoted_candidates` explicitly lists `"universal factor sweep claim after Goal4134 factor-0.25-only 524k extension"`.

The `CURRENT_BENCHMARK_ROUTE_DECISION_VERSION` is `"rtdl.v2_10.current_benchmark_route_decisions.goal4135.v1"`, correctly advancing from the `goal4131.v1` version. ✓

---

### 8. Are there correctness, determinism, scale-sensitivity, app-agnostic, or performance-risk issues that should block the next RT-DBSCAN engineering step?

**Answer: accept — no blocking issues identified.**

The following non-blocking observations are noted for the engineering record.

**Non-blocking: road3d replay and one-shot speedups both decline monotonically at 524k.** Replay series: 65k 1.866x → 131k 1.545x → 262k 1.428x → 524k 1.367x. One-shot series: 65k 2.609x → 131k 2.606x → 262k 2.272x → 524k 1.910x. Both trends are monotonically declining. The 524k values remain clearly positive (1.367x replay, 1.910x one-shot total), but road3d should be an explicit priority if a 1M-point probe is added. This observation was made in Goal4132/Goal4133 reviews and is confirmed by the new data point.

**Non-blocking: Tie-break semantics for equidistant queries (carry-forward from prior reviews).** The advisor sort by `(distance, -metric, factor)` is deterministic for all currently tested entries because speedup values differ at each equidistant pair. The two 65k ngsim_dense entries are correctly distinguished by the metric key. A future probe at a scale equidistant between two existing entries with identical metric values would require tiebreaking by insertion order — this should be addressed before the evidence table grows beyond five entries per profile.

**Non-blocking: `plan_rt_dbscan_execution` remains on Goal2425 evidence.** Structurally unchanged and intentionally separate. The divergence should be noted if future guidance consolidation is attempted.

---

## Summary

| Goal | Finding |
|---|---|
| 4134 runner scope | Confirmed: single factor `[0.25]`, 524,288 points, `repeat=2`, `warmup=1`, schema `rtdl.goal4117.partition_cell_factor_route_sweep.v1`, commit `93c52cb1`, clean worktree. |
| 4134 speedup values | All six values (`3.291x`, `3.250x`, `1.367x`, `1.910x`, `1.769x`, `2.489x`) verified exactly against JSON raw fields and arithmetic cross-checks. |
| 4134 signature preservation | `same_signature: true` and `all_factors_match_current_signature: true` on all three factor-profile rows. No sub-parity rows at 524k with factor 0.25. |
| 4135 extension framing | Correctly framed as factor-0.25-only extension; `"universal factor sweep claim"` listed in `rejected_or_unpromoted_candidates`. |
| 4135 advisor asymmetry handling | `metric_key` correctly surfaces factor `0.5` for repeated and factor `0.25` for one-shot at 65k ngsim_dense; `user_choice_guidance` makes the asymmetry explicit. Sort is deterministic for all current entries. |
| 4135 advisory enforcement | All advisory enforcement flags intact; no dispatch surface added; `__post_init__` enforces all nine prohibited flags; `validate_current_benchmark_route_decisions()` returns `accept`, `errors == ()`. |
| `plan_rt_dbscan_execution` separation | Confirmed unchanged; structurally separate from the advisor; Goal2425 evidence only. |
| Claim boundaries | All prohibited flags are `False` across JSON pod, advisor packet, and registry. Structural enforcement via `__post_init__` and validator pass. |

**Verdict: `accept-with-boundary`**

Goals 4134–4135 cleanly extend the Goal4117/Goal4122/Goal4126/Goal4130 evidence chain to the 524k scale for factor 0.25 only. The probe is commit-pinned to `93c52cb1` with a clean worktree, the single tested factor is clearly scoped and not over-claimed, and all six reported speedup values are exactly supported by the JSON artifact. The advisor correctly distinguishes repeated replay ranking from one-shot total ranking for the 65k ngsim_dense asymmetry (factor 0.5 for replay, factor 0.25 for one-shot total), and the route registry explicitly rejects a universal factor sweep claim. All claim boundaries are intact across the JSON pod, advisor packet, and registry, with structural enforcement via `__post_init__` and the validator returning `accept` with zero errors. The three non-blocking observations (road3d monotonic decline, tie-break semantics, `plan_rt_dbscan_execution` divergence) do not block the next RT-DBSCAN engineering step.

This review does not authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, hidden dispatch, automatic partner selection, automatic factor selection, native ABI additions, AMD performance claims, or true-zero-copy claims.
